import os
import requests
import logging
import psycopg2
from datetime import datetime
from psycopg2 import sql
import time  # Import time module to add delay

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Get the OpenWeather API key and PostgreSQL connection details from environment variables
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
        conn = psycopg2.connect(
            host=DB_HOST,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        logger.error(f"Error connecting to the database: {e}")
        exit(1)

# Function to create the weather_data table if it doesn't exist
def create_table_if_not_exists(cursor):
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
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    '''
    cursor.execute(create_table_query)

# Function to save weather data to the PostgreSQL database
def save_weather_data(weather_data):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create table if it doesn't exist
    create_table_if_not_exists(cursor)

    insert_query = sql.SQL("""
        INSERT INTO weather_data (
            city, country, latitude, longitude, temperature, feels_like,
            humidity, pressure, wind_speed, wind_direction, description, visibility,
            is_daytime
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """)

    cursor.execute(insert_query, (
        weather_data["city"],
        weather_data["country"],
        weather_data["latitude"],
        weather_data["longitude"],
        weather_data["temperature"],
        weather_data["feels_like"],
        weather_data["humidity"],
        weather_data["pressure"],
        weather_data["wind_speed"],
        weather_data["wind_direction"],
        weather_data["description"],
        weather_data["visibility"],
        weather_data["is_daytime"]
    ))

    conn.commit()
    cursor.close()
    conn.close()
    logger.info(f"Weather data for {weather_data['city']} saved successfully.")

# Function to get weather data from the OpenWeather API
def get_weather(city):
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

    logger.info(f"Fetching weather data for {city}")
    try:
        response = requests.get(BASE_URL, params=params)
        if response.status_code == 200:
            logger.info(f"Successfully fetched weather data for {city}")
            data = response.json()

            # Convert timestamps to datetime objects
            sunrise = datetime.utcfromtimestamp(data["sys"]["sunrise"])
            sunset = datetime.utcfromtimestamp(data["sys"]["sunset"])
            current_time = datetime.utcfromtimestamp(data["dt"])

            weather_info = {
                "city": city,
                "country": data["sys"]["country"],
                "latitude": data["coord"]["lat"],
                "longitude": data["coord"]["lon"],
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "wind_speed": data["wind"]["speed"],
                "wind_direction": data["wind"]["deg"],
                "description": data["weather"][0]["description"],
                "visibility": data.get("visibility", 0),  # Default to 0 if not available
                "is_daytime": sunrise < current_time < sunset  # Check if current time is between sunrise and sunset
            }

            return weather_info
        else:
            logger.error(f"Failed to fetch weather data for {city} - Status Code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error occurred while fetching weather data for {city}: {e}")
        return None

# Main function to loop through cities and fetch/save the weather data
def main():
    while True:  # Keep the loop running indefinitely
        for city in CITIES:
            weather_data = get_weather(city)
            if weather_data:
                save_weather_data(weather_data)
            else:
                logger.error(f"No weather data available for {city}")
        
        logger.info("Waiting for 2 minutes before fetching again.")
        time.sleep(120)  # Wait for 2 minutes before fetching again

if __name__ == "__main__":
    main()
