
log into clickhouse db

clickhouse-client -h clickhouse-host
clickhouse-client -u admin --password password
SHOW DATABASES;
USE clickhouse_db;
SELECT * FROM clickhouse_db.weather_info limit 10;


SELECT city, recorded_at, temperature, 
       temperature - lagInFrame(temperature) OVER (PARTITION BY city ORDER BY recorded_at) AS temp_change
FROM clickhouse_db.weather_info
ORDER BY temp_change ASC
LIMIT 5;

SELECT description, COUNT(*) AS occurrences
FROM clickhouse_db.weather_info
GROUP BY description
ORDER BY occurrences DESC;

SELECT * FROM clickhouse_db.weather_info
WHERE recorded_at >= now() - INTERVAL 1 DAY
ORDER BY recorded_at DESC;

SELECT city, temperature, description
FROM clickhouse_db.weather_info
WHERE is_daytime = 0
ORDER BY recorded_at DESC;

SELECT city, country, wind_speed
FROM clickhouse_db.weather_info
ORDER BY wind_speed DESC
LIMIT 5;

SELECT country, COUNT(*) AS record_count
FROM clickhouse_db.weather_info
GROUP BY country
ORDER BY record_count DESC;

SELECT 
    city, 
    AVG(temperature) AS avg_temp, 
    AVG(feels_like) AS avg_feels_like, 
    AVG(humidity) AS avg_humidity, 
    AVG(pressure) AS avg_pressure
FROM clickhouse_db.weather_info
WHERE city = 'New York'
GROUP BY city;

SELECT city, country, temperature 
FROM clickhouse_db.weather_info 
ORDER BY temperature DESC 
LIMIT 5;  -- Hottest

SELECT city, country, temperature 
FROM clickhouse_db.weather_info 
ORDER BY temperature ASC 
LIMIT 5;  -- Coldest

SELECT * FROM clickhouse_db.weather_info 
ORDER BY recorded_at DESC 
LIMIT 10;




