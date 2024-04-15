import requests
import psycopg2
from datetime import datetime
import json
import time

def connect_to_database():
    # Connect to the PostgreSQL database
    try:
        conn = psycopg2.connect(
            dbname="bcweather",
            user="rmtk",
            password="your_password",
            host="localhost"
        )
        print("Connected to the database")
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        return None

def create_weather_table(conn):
    try:
        # Create the table
        with conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS WeatherData (
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
                )
                """
            )
        conn.commit()
        print("Table 'WeatherData' created successfully")
    except psycopg2.Error as e:
        print(f"Error creating table: {e}")

def insert_weather_data(conn, location_id, weather_data):
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO WeatherData (
                    location_id, weather, base, main_temp, main_feels_like,
                    main_temp_min, main_temp_max, main_pressure, main_humidity,
                    main_sea_level, main_grnd_level, visibility, wind_speed,
                    wind_deg, wind_gust, clouds_all, rain_1h, rain_3h,
                    snow_1h, snow_3h, dt, sys_sunrise, sys_sunset, timezone
                )
                VALUES (
                    %s, %s::jsonb, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                """,
                (
                    location_id, json.dumps(weather_data.get('weather')), weather_data.get('base'),
                    weather_data.get('main', {}).get('temp'), weather_data.get('main', {}).get('feels_like'),
                    weather_data.get('main', {}).get('temp_min'), weather_data.get('main', {}).get('temp_max'),
                    weather_data.get('main', {}).get('pressure'), weather_data.get('main', {}).get('humidity'),
                    weather_data.get('main', {}).get('sea_level'), weather_data.get('main', {}).get('grnd_level'),
                    weather_data.get('visibility'), weather_data.get('wind', {}).get('speed'),
                    weather_data.get('wind', {}).get('deg'), weather_data.get('wind', {}).get('gust'),
                    weather_data.get('clouds', {}).get('all'), weather_data.get('rain', {}).get('1h'),
                    weather_data.get('rain', {}).get('3h'), weather_data.get('snow', {}).get('1h'),
                    weather_data.get('snow', {}).get('3h'),
                    datetime.fromtimestamp(weather_data.get('dt')),
                    datetime.fromtimestamp(weather_data.get('sys', {}).get('sunrise')),
                    datetime.fromtimestamp(weather_data.get('sys', {}).get('sunset')),
                    weather_data.get('timezone')
                )
            )
        conn.commit()
        print("Weather data inserted successfully")
    except psycopg2.Error as e:
        print(f"Error inserting weather data: {e}")

def call_weather_api(lat, lon, api_key):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def main():
    delay = 3600
    api_key = 'API_KEY'
    conn = connect_to_database()

    if conn is not None:
        create_weather_table(conn)

        try:
            while True:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM Locations")
                    rows = cursor.fetchall()

                    for row in rows:
                        stop_id, lat, lon, _, _, _, _, stop_name = row

                        if lat == 0 or lon == 0:
                            print(f"Ignoring row for bus stop {stop_name}: Latitude or longitude is zero.")
                            continue

                        weather_data = call_weather_api(lat, lon, api_key)

                        if weather_data:
                            insert_weather_data(conn, stop_id, weather_data)
                        else:
                            print(f"Failed to fetch weather forecast for bus stop {stop_name}.")
                print(f"Sleeping for {delay}s")            
                time.sleep(delay)               
        except psycopg2.Error as e:
            print(f"Error executing SQL query: {e}")
        finally:
            conn.close()
    else:
        print("Unable to connect to the database")

if __name__ == "__main__":
    main()
