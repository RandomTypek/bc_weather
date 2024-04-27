import requests
import psycopg2
from datetime import datetime
import json
import time
import sys

def load_config(filename):
    """
    Load configuration settings from a JSON file.

    Args:
        filename (str): The path to the JSON configuration file.

    Returns:
        dict: Configuration settings.
    """
    
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Config file '{filename}' not found.")
        sys.stdout.flush()
        return None
        
def connect_to_database(config):
    """
    Connect to the PostgreSQL database.

    Args:
        config (dict): Database connection parameters.

    Returns:
        psycopg2.connection: Connection object if successful, None otherwise.
    """
    
    # Connect to the PostgreSQL database
    try:
        conn = psycopg2.connect(
            dbname=config['dbname'],
            user=config['user'],
            password=config['password'],
            host=config['host']
        )
        print("Connected to the database")
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        sys.stdout.flush()
        return None

def create_weather_table(conn):
    """
    Create the 'WeatherData' table in the database if it doesn't exist.

    Args:
        conn (psycopg2.connection): Connection object to the PostgreSQL database.
    """
    
    try:
        # Create the table
        with conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS WeatherData (
                    weather_id SERIAL PRIMARY KEY,
                    location_id INT REFERENCES Locations(stop_id),
                    weather JSONB,
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
        sys.stdout.flush()
    except psycopg2.Error as e:
        print(f"Error creating table: {e}")
        sys.stdout.flush()

def insert_weather_data(conn, location_id, weather_data):
    """
    Insert weather data into the 'WeatherData' table.

    Args:
        conn (psycopg2.connection): Connection object to the PostgreSQL database.
        location_id (int): ID of the location.
        weather_data (dict): Weather data to be inserted.
    """
    
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO WeatherData (
                    location_id, weather, main_temp, main_feels_like,
                    main_temp_min, main_temp_max, main_pressure, main_humidity,
                    main_sea_level, main_grnd_level, visibility, wind_speed,
                    wind_deg, wind_gust, clouds_all, rain_1h, rain_3h,
                    snow_1h, snow_3h, dt, sys_sunrise, sys_sunset, timezone
                )
                VALUES (
                    %s, %s::jsonb, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                """,
                (
                    location_id, json.dumps(weather_data.get('weather')),
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
        sys.stdout.flush()

def call_weather_api(lat, lon, api_key):
    """
    Call the OpenWeatherMap API to fetch weather data.

    Args:
        lat (float): Latitude of the location.
        lon (float): Longitude of the location.
        api_key (str): API key for accessing the OpenWeatherMap API.

    Returns:
        dict: Weather data in JSON format.
    """
    
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        sys.stdout.flush()
        return None

def main():
    config = load_config('config.json')
    if config is None:
        return

    delay = config.get('delay', 3600)
    api_key = config.get('api_key')
    conn = connect_to_database(config)

    if conn is not None:
        create_weather_table(conn)

        try:
            while True:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM Locations") # Fetch all locations from the database
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
                            sys.stdout.flush()
                print(f"Sleeping for {delay}s")            
                time.sleep(delay)               
        except psycopg2.Error as e:
            print(f"Error executing SQL query: {e}")
            sys.stdout.flush()
        finally:
            conn.close()
    else:
        print("Unable to connect to the database")
        sys.stdout.flush()

if __name__ == "__main__":
    main()