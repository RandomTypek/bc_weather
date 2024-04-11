CREATE TABLE Locations (
    stop_id INT PRIMARY KEY,
    latitude DECIMAL,
    longitude DECIMAL,
    state VARCHAR(3),
    region VARCHAR(3),
    town VARCHAR(100),
    town_part VARCHAR(100),
    stop_name VARCHAR(100)
);

CREATE TABLE WeatherData (
    weather_id SERIAL PRIMARY KEY,
    location_id INT REFERENCES Locations(stop_id),
    weather JSONB,
    base VARCHAR(50),
    main_temp DECIMAL,
    main_feels_like DECIMAL,
    main_temp_min DECIMAL,
    main_temp_max DECIMAL,
    main_pressure INT,
    main_humidity INT,
    main_sea_level INT,
    main_grnd_level INT,
    visibility INT,
    wind_speed DECIMAL,
    wind_deg INT,
    wind_gust DECIMAL,
    clouds_all INT,
    rain_1h DECIMAL,
    rain_3h DECIMAL,
    snow_1h DECIMAL,
    snow_3h DECIMAL,
    dt TIMESTAMP,
    sys_sunrise TIMESTAMP,
    sys_sunset TIMESTAMP,
    timezone INT
);
