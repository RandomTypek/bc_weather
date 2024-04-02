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
    dt TIMESTAMP,
    sunrise TIMESTAMP,
    sunset TIMESTAMP,    
    temp DECIMAL,
    feels_like DECIMAL,
    pressure INT,
    humidity INT,
    dew_point DECIMAL,
    uvi DECIMAL,
    clouds INT,
    visibility INT,
    wind_speed DECIMAL,
    wind_deg INT,
    wind_gust DECIMAL,
    rain_1h INT,
    snow_1h INT,
    current_weather_id INT,
    current_weather_main VARCHAR(100),
    current_weather_description VARCHAR(255),
    current_weather_icon VARCHAR(20)
);
