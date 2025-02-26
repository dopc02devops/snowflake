CREATE DATABASE IF NOT EXISTS clickhouse_db;

CREATE TABLE IF NOT EXISTS clickhouse_db.weather_data (
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
    created_at DateTime DEFAULT now(),
    trace_id VARCHAR(255)
) ENGINE = MergeTree()
ORDER BY (country, city, created_at)  -- Optimize for common queries
PARTITION BY toYYYYMM(created_at)  -- Monthly partitions
TTL created_at + INTERVAL 1 YEAR DELETE  -- Auto-delete old data
SETTINGS index_granularity = 8192;
