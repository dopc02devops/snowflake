-- Log into ClickHouse DB
clickhouse-client -h clickhouse-host
clickhouse-client -u admin --password password

-- Show available databases
SHOW DATABASES;

-- Show tables in the weather_data database
SHOW TABLES FROM weather_data;

-- Use the weather_data database
USE weather_data;

-- Get the count of rows in the raw weather stream data
SELECT COUNT(*) FROM weather_data.clickhouse_db_raw__stream_weather_data;

-- Get the Latest Weather Data per City
WITH ranked_data AS (
    SELECT 
        JSONExtractString(_airbyte_data, 'city') AS city,
        JSONExtractString(_airbyte_data, 'country') AS country,
        JSONExtractFloat(_airbyte_data, 'temperature') AS temperature,
        JSONExtractInt(_airbyte_data, 'humidity') AS humidity,
        JSONExtractFloat(_airbyte_data, 'wind_speed') AS wind_speed,
        JSONExtractString(_airbyte_data, 'description') AS description,
        JSONExtractString(_airbyte_data, 'created_at') AS created_at,
        ROW_NUMBER() OVER (PARTITION BY JSONExtractString(_airbyte_data, 'city') ORDER BY JSONExtractString(_airbyte_data, 'created_at') DESC) AS row_num
    FROM weather_data.clickhouse_db_raw__stream_weather_data
)
SELECT * FROM ranked_data WHERE row_num = 1;

-- Extract Structured Weather Data
SELECT 
    JSONExtractInt(_airbyte_data, 'id') AS id,
    JSONExtractString(_airbyte_data, 'city') AS city,
    JSONExtractString(_airbyte_data, 'country') AS country,
    JSONExtractFloat(_airbyte_data, 'latitude') AS latitude,
    JSONExtractFloat(_airbyte_data, 'longitude') AS longitude,
    JSONExtractFloat(_airbyte_data, 'temperature') AS temperature,
    JSONExtractFloat(_airbyte_data, 'feels_like') AS feels_like,
    JSONExtractInt(_airbyte_data, 'humidity') AS humidity,
    JSONExtractInt(_airbyte_data, 'pressure') AS pressure,
    JSONExtractFloat(_airbyte_data, 'wind_speed') AS wind_speed,
    JSONExtractInt(_airbyte_data, 'wind_direction') AS wind_direction,
    JSONExtractString(_airbyte_data, 'description') AS description,
    JSONExtractInt(_airbyte_data, 'visibility') AS visibility,
    JSONExtractBool(_airbyte_data, 'is_daytime') AS is_daytime,
    JSONExtractString(_airbyte_data, 'created_at') AS created_at
FROM weather_data.clickhouse_db_raw__stream_weather_data;

-- Find Cities with the Highest Temperature
SELECT 
    JSONExtractString(_airbyte_data, 'city') AS city,
    JSONExtractString(_airbyte_data, 'country') AS country,
    MAX(JSONExtractFloat(_airbyte_data, 'temperature')) AS max_temperature
FROM weather_data.clickhouse_db_raw__stream_weather_data
GROUP BY city, country
ORDER BY max_temperature DESC
LIMIT 10;

-- Find the Windiest Locations
SELECT 
    JSONExtractString(_airbyte_data, 'city') AS city,
    JSONExtractString(_airbyte_data, 'country') AS country,
    MAX(JSONExtractFloat(_airbyte_data, 'wind_speed')) AS max_wind_speed
FROM weather_data.clickhouse_db_raw__stream_weather_data
GROUP BY city, country
ORDER BY max_wind_speed DESC
LIMIT 10;

-- Check Weather Conditions for a Specific City (e.g., Buea)
SELECT 
    JSONExtractString(_airbyte_data, 'created_at') AS timestamp,
    JSONExtractFloat(_airbyte_data, 'temperature') AS temperature,
    JSONExtractInt(_airbyte_data, 'humidity') AS humidity,
    JSONExtractInt(_airbyte_data, 'pressure') AS pressure,
    JSONExtractFloat(_airbyte_data, 'wind_speed') AS wind_speed,
    JSONExtractString(_airbyte_data, 'description') AS weather_condition
FROM weather_data.clickhouse_db_raw__stream_weather_data
WHERE JSONExtractString(_airbyte_data, 'city') = 'Buea'
ORDER BY timestamp DESC
LIMIT 10;

-- Find Cities with Heavy Rain Forecasts
SELECT 
    JSONExtractString(_airbyte_data, 'city') AS city,
    JSONExtractString(_airbyte_data, 'country') AS country,
    JSONExtractFloat(_airbyte_data, 'temperature') AS temperature,
    JSONExtractInt(_airbyte_data, 'humidity') AS humidity,
    JSONExtractFloat(_airbyte_data, 'wind_speed') AS wind_speed,
    JSONExtractString(_airbyte_data, 'description') AS weather_condition,
    JSONExtractString(_airbyte_data, 'created_at') AS timestamp
FROM weather_data.clickhouse_db_raw__stream_weather_data
WHERE JSONExtractString(_airbyte_data, 'description') LIKE '%rain%'
ORDER BY timestamp DESC
LIMIT 10;

-- Find Cities with Clear and Sunny Weather
SELECT 
    JSONExtractString(_airbyte_data, 'city') AS city,
    JSONExtractString(_airbyte_data, 'country') AS country,
    JSONExtractFloat(_airbyte_data, 'temperature') AS temperature,
    JSONExtractInt(_airbyte_data, 'humidity') AS humidity,
    JSONExtractFloat(_airbyte_data, 'wind_speed') AS wind_speed,
    JSONExtractString(_airbyte_data, 'description') AS weather_condition,
    JSONExtractString(_airbyte_data, 'created_at') AS timestamp
FROM weather_data.clickhouse_db_raw__stream_weather_data
WHERE JSONExtractString(_airbyte_data, 'description') LIKE '%clear sky%'
ORDER BY timestamp DESC
LIMIT 10;

-- Find Locations with Extreme Weather Conditions (High Winds, Low Visibility)
SELECT 
    JSONExtractString(_airbyte_data, 'city') AS city,
    JSONExtractString(_airbyte_data, 'country') AS country,
    JSONExtractFloat(_airbyte_data, 'temperature') AS temperature,
    JSONExtractInt(_airbyte_data, 'humidity') AS humidity,
    JSONExtractFloat(_airbyte_data, 'wind_speed') AS wind_speed,
    JSONExtractInt(_airbyte_data, 'visibility') AS visibility,
    JSONExtractString(_airbyte_data, 'description') AS weather_condition,
    JSONExtractString(_airbyte_data, 'created_at') AS timestamp
FROM weather_data.clickhouse_db_raw__stream_weather_data
WHERE JSONExtractFloat(_airbyte_data, 'wind_speed') > 10  -- High winds
   OR JSONExtractInt(_airbyte_data, 'visibility') < 2000  -- Low visibility
ORDER BY timestamp DESC
LIMIT 10;

-- Find Locations with High Temperatures & High Humidity (Heatwave Conditions)
SELECT 
    JSONExtractString(_airbyte_data, 'city') AS city,
    JSONExtractString(_airbyte_data, 'country') AS country,
    JSONExtractFloat(_airbyte_data, 'temperature') AS temperature,
    JSONExtractInt(_airbyte_data, 'humidity') AS humidity,
    JSONExtractString(_airbyte_data, 'description') AS weather_condition,
    JSONExtractString(_airbyte_data, 'created_at') AS timestamp
FROM weather_data.clickhouse_db_raw__stream_weather_data
WHERE JSONExtractFloat(_airbyte_data, 'temperature') > 35  -- High temperature threshold
  AND JSONExtractInt(_airbyte_data, 'humidity') > 70  -- High humidity threshold
ORDER BY timestamp DESC
LIMIT 10;

-- Find the Most Recent Weather Reports for Each City
WITH latest_weather AS (
    SELECT 
        JSONExtractString(_airbyte_data, 'city') AS city,
        JSONExtractString(_airbyte_data, 'country') AS country,
        JSONExtractFloat(_airbyte_data, 'temperature') AS temperature,
        JSONExtractInt(_airbyte_data, 'humidity') AS humidity,
        JSONExtractString(_airbyte_data, 'description') AS weather_condition,
        JSONExtractString(_airbyte_data, 'created_at') AS timestamp,
        ROW_NUMBER() OVER (PARTITION BY JSONExtractString(_airbyte_data, 'city') ORDER BY JSONExtractString(_airbyte_data, 'created_at') DESC) AS row_num
    FROM weather_data.clickhouse_db_raw__stream_weather_data
)
SELECT * FROM latest_weather WHERE row_num = 1;
