DROP TABLE IF EXISTS fact_properties;
DROP TABLE IF EXISTS dim_luxury_segment;
DROP TABLE IF EXISTS dim_time;
DROP TABLE IF EXISTS dim_source;
DROP TABLE IF EXISTS dim_property_type;
DROP TABLE IF EXISTS dim_neighborhood;
DROP TABLE IF EXISTS dim_city;

CREATE TABLE dim_city (
    city_id INTEGER PRIMARY KEY,
    city VARCHAR(150) NOT NULL,
    country VARCHAR(100) NOT NULL
);

CREATE TABLE dim_neighborhood (
    neighborhood_id INTEGER PRIMARY KEY,
    neighborhood VARCHAR(150) NOT NULL,
    city_id INTEGER NOT NULL,
    FOREIGN KEY (city_id) REFERENCES dim_city(city_id)
);

CREATE TABLE dim_property_type (
    property_type_id INTEGER PRIMARY KEY,
    property_type VARCHAR(100) NOT NULL
);

CREATE TABLE dim_source (
    source_id INTEGER PRIMARY KEY,
    source VARCHAR(150) NOT NULL
);

CREATE TABLE dim_time (
    time_id INTEGER PRIMARY KEY,
    scraping_date TIMESTAMP NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    day INTEGER NOT NULL,
    day_name VARCHAR(20) NOT NULL,
    is_weekend BOOLEAN NOT NULL
);

CREATE TABLE dim_luxury_segment (
    luxury_segment_id INTEGER PRIMARY KEY,
    luxury_label VARCHAR(50) NOT NULL
);

CREATE TABLE fact_properties (
    fact_id INTEGER PRIMARY KEY,
    city_id INTEGER NOT NULL,
    neighborhood_id INTEGER NOT NULL,
    property_type_id INTEGER NOT NULL,
    source_id INTEGER NOT NULL,
    time_id INTEGER NOT NULL,
    luxury_segment_id INTEGER NOT NULL,
    source_record_id VARCHAR(150) NOT NULL,
    load_timestamp TIMESTAMP NOT NULL,
    price_eur DECIMAL(14,2) NOT NULL,
    area_m2 DECIMAL(12,2) NOT NULL,
    bedrooms DECIMAL(8,2),
    bathrooms DECIMAL(8,2),
    price_per_m2 DECIMAL(14,2) NOT NULL,
    luxury_threshold_country DECIMAL(14,2) NOT NULL,
    FOREIGN KEY (city_id) REFERENCES dim_city(city_id),
    FOREIGN KEY (neighborhood_id) REFERENCES dim_neighborhood(neighborhood_id),
    FOREIGN KEY (property_type_id) REFERENCES dim_property_type(property_type_id),
    FOREIGN KEY (source_id) REFERENCES dim_source(source_id),
    FOREIGN KEY (time_id) REFERENCES dim_time(time_id),
    FOREIGN KEY (luxury_segment_id) REFERENCES dim_luxury_segment(luxury_segment_id)
);
