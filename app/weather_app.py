import os
import requests
import logging
import psycopg2
from datetime import datetime
from psycopg2 import sql
import time
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from prometheus_client import start_http_server, Counter, Histogram
import warnings
from urllib3.exceptions import InsecureRequestWarning

# Suppress SSL warnings for debugging (not recommended for production)
warnings.simplefilter('ignore', InsecureRequestWarning)

# Initialize logging early to capture all logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Set up OpenTelemetry with a defined service name
resource = Resource.create({"service.name": "weather_service"})
provider = TracerProvider(resource=resource)
trace.set_tracer_provider(provider)

# Set up OTLP exporter for OpenTelemetry
otlp_exporter = OTLPSpanExporter(endpoint="http://otel-collector:4317", timeout=5)
span_processor = BatchSpanProcessor(otlp_exporter)
provider.add_span_processor(span_processor)
provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

# Create a global tracer
tracer = trace.get_tracer("weather_service.tracer")

# Prometheus metrics setup
REQUEST_COUNTER = Counter('weather_service_requests_total', 'Total number of requests to the weather app')
RESPONSE_TIME_HISTOGRAM = Histogram('weather_service_response_duration_seconds', 'Histogram of response durations')

# Get environment variables
API_KEY = os.getenv("OPENWEATHER_API_KEY")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "weather_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "mysecretpassword")

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
CITIES = ["Buea", "Limbe", "Kumba", "Tiko", "Mutengene", "Tombel", "Mamfe"]

if not API_KEY:
    logger.error("API Key is missing! Please set the OPENWEATHER_API_KEY environment variable.")
    exit(1)

# Function to connect to the PostgreSQL database
def get_db_connection():
    try:
        with tracer.start_as_current_span("db_connection"):
            logger.info("Connecting to the database...")
            conn = psycopg2.connect(
                host=DB_HOST,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )
            logger.info("Database connection successful.")
            return conn
    except Exception as e:
        logger.error(f"Error connecting to the database: {e}")
        exit(1)

# Function to create the weather_data table
def create_table_if_not_exists(cursor):
    logger.info("Ensuring the weather_data table exists...")
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS weather_data (
        id SERIAL PRIMARY KEY,
        city VARCHAR(255) NOT NULL,
        country VARCHAR(255) NOT NULL,
        latitude FLOAT NOT NULL,
        longitude FLOAT NOT NULL,
        temperature FLOAT NOT NULL,
        feels_like FLOAT NOT NULL,
        humidity INT NOT NULL,
        pressure INT NOT NULL,
        wind_speed FLOAT NOT NULL,
        wind_direction INT NOT NULL,
        description TEXT NOT NULL,
        visibility INT NOT NULL,
        is_daytime BOOLEAN NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        trace_id VARCHAR(255) -- or VARCHAR(32) or CHAR(32)
    );
    '''
    cursor.execute(create_table_query)
    logger.info("Table check complete.")

# Function to save weather data to PostgreSQL
def save_weather_data(weather_data, trace_id):
    logger.info(f"Saving weather data for {weather_data.get('city', 'Unknown')} [trace_id={trace_id}]")
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            create_table_if_not_exists(cursor)
            insert_query = sql.SQL("""
                INSERT INTO weather_data (
                    city, country, latitude, longitude, temperature, feels_like,
                    humidity, pressure, wind_speed, wind_direction, description, visibility,
                    is_daytime, created_at, trace_id
                ) VALUES ({})
            """).format(
                sql.SQL(',').join([sql.Placeholder()] * 15)  # 14 fields + trace_id
            )
            
            created_at = datetime.utcnow().isoformat()
            values = (
                weather_data.get("city", ""),
                weather_data.get("country", ""),
                weather_data.get("latitude", 0.0),
                weather_data.get("longitude", 0.0),
                weather_data.get("temperature", 0.0),
                weather_data.get("feels_like", 0.0),
                weather_data.get("humidity", 0),
                weather_data.get("pressure", 0),
                weather_data.get("wind_speed", 0.0),
                weather_data.get("wind_direction", 0),
                weather_data.get("description", ""),
                weather_data.get("visibility", 0),
                weather_data.get("is_daytime", False),
                created_at,
                trace_id  # Include the trace_id here
            )
            
            # Execute the query
            cursor.execute(insert_query, values)
            conn.commit()
            logger.info(f"Weather data for {weather_data.get('city', 'Unknown city')} saved successfully [trace_id={trace_id}].")

# Function to get weather data from API
def get_weather(city):
    with tracer.start_as_current_span("weather_request") as span:
        trace_id = format(span.get_span_context().trace_id, '032x')[-32:]  # Extract trace_id
        logger.info(f"Fetching weather data for {city} [trace_id={trace_id}]")
        params = {"q": city, "appid": API_KEY, "units": "metric"}
        try:
            start_time = time.time()
            response = requests.get(BASE_URL, params=params, timeout=10, verify=False)
            RESPONSE_TIME_HISTOGRAM.observe(time.time() - start_time)
            
            if response.status_code == 200:
                weather_data = response.json()
                
                # Check if the response has the necessary keys
                if 'city' not in weather_data:
                    logger.error(f"Missing 'city' in the weather data response for {city}. Response: {weather_data} [trace_id={trace_id}]")
                    return None
                
                logger.info(f"Weather data for {city} fetched successfully [trace_id={trace_id}].")
                save_weather_data(weather_data, trace_id)  # Pass trace_id to save_weather_data
                return weather_data
            else:
                logger.error(f"Failed to fetch weather data for {city} [trace_id={trace_id}]. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching weather data for {city}: {e} [trace_id={trace_id}]")
        return None

start_http_server(9089)

def main():
    while True:
        for city in CITIES:
            weather_data = get_weather(city)
            if weather_data:
                save_weather_data(weather_data, "no_trace_id")  # Use a default if no trace_id is available
        time.sleep(120)

if __name__ == "__main__":
    main()
