CREATE DATABASE IF NOT EXISTS clickhouse_db;

CREATE TABLE IF NOT EXISTS clickhouse_db.weather_info (
    city String,
    country String,
    latitude Float64,
    longitude Float64,
    temperature Float32,
    feels_like Float32,
    humidity UInt8,
    pressure UInt16,
    wind_speed Float32,
    wind_direction UInt16,
    description String,
    visibility UInt32 DEFAULT 0,
    is_daytime Boolean,
    recorded_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY recorded_at;
