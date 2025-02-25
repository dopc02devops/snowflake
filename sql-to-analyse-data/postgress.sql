-- Log into PostgreSQL
psql -h localhost -U postgres -d weather_db

-- Show the list of tables in the current database
\dt

-- Select the first 10 records from the weather_data table
SELECT * FROM weather_data LIMIT 10;

-- To check the structure (schema) of the 'weather_data' table
\d weather_data

-- To count the number of records in the 'weather_data' table
SELECT COUNT(*) FROM weather_data;

-- To retrieve weather data for a specific city (e.g., Buea)
SELECT * FROM weather_data WHERE city = 'Buea' LIMIT 10;

-- To find cities with the highest temperature
SELECT city, country, MAX(temperature) AS max_temperature
FROM weather_data
GROUP BY city, country
ORDER BY max_temperature DESC
LIMIT 10;

-- To find the windiest locations (max wind speed)
SELECT city, country, MAX(wind_speed) AS max_wind_speed
FROM weather_data
GROUP BY city, country
ORDER BY max_wind_speed DESC
LIMIT 10;

-- To check the weather conditions for a specific time frame
SELECT * FROM weather_data WHERE created_at >= '2025-02-01' AND created_at <= '2025-02-28';

-- To retrieve cities with heavy rain conditions (using a weather description)
SELECT city, country, temperature, humidity, wind_speed, description
FROM weather_data
WHERE description LIKE '%rain%'
ORDER BY created_at DESC
LIMIT 10;

-- To retrieve cities with clear and sunny weather
SELECT city, country, temperature, humidity, wind_speed, description
FROM weather_data
WHERE description LIKE '%clear sky%'
ORDER BY created_at DESC
LIMIT 10;

-- To find locations with extreme weather conditions (high winds and low visibility)
SELECT city, country, temperature, humidity, wind_speed, visibility, description
FROM weather_data
WHERE wind_speed > 10 OR visibility < 2000
ORDER BY created_at DESC
LIMIT 10;

-- To find locations with heatwave conditions (high temperatures and humidity)
SELECT city, country, temperature, humidity, description
FROM weather_data
WHERE temperature > 35 AND humidity > 70
ORDER BY created_at DESC
LIMIT 10;

-- To get the most recent weather report for each city
WITH latest_weather AS (
    SELECT city, country, temperature, humidity, description, created_at,
           ROW_NUMBER() OVER (PARTITION BY city ORDER BY created_at DESC) AS row_num
    FROM weather_data
)
SELECT * FROM latest_weather WHERE row_num = 1;
