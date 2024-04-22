import psycopg2
import requests
from datetime import datetime
import json

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

def fetch_locations_from_database(db_config):
    try:
        conn = psycopg2.connect(
            dbname=db_config["dbname"],
            user=db_config["user"],
            password=db_config["password"],
            host=db_config["host"]
        )
        cursor = conn.cursor()
        cursor.execute("SELECT latitude, longitude FROM Locations")
        locations = cursor.fetchall()
        return locations
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL database: {e}")
        return None
    finally:
        if conn is not None:
            conn.close()

def load_config():
    try:
        with open('config.json') as f:
            config = json.load(f)
            return config
    except FileNotFoundError:
        print("Config file not found.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in config file: {e}")
        return None

def main():
    config = load_config()

    if config:
        api_key = config["api_key"]
        db_config = {
            "dbname": config["dbname"],
            "user": config["user"],
            "password": config["password"],
            "host": config["host"]
        }

        # Fetch locations from the database
        locations = fetch_locations_from_database(db_config)

        if locations:
            for location in locations:
                lat, lon = location
                # Ignore rows with zero latitude or longitude
                if lat == 0 or lon == 0:
                    print(f"Ignoring row: Latitude or longitude is zero.")
                    continue
                weather_data = call_weather_api(lat, lon, api_key)
                if weather_data:
                    current_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                    print(f"Weather data fetched successfully at {current_time} for location ({lat}, {lon}).")
                    for key, value in weather_data.items():
                        if isinstance(value, dict):
                            for sub_key, sub_value in value.items():
                                print(f"{key}.{sub_key}: {sub_value}")
                        else:
                            print(f"{key}: {value}")
                else:
                    print(f"Failed to fetch weather forecast for location ({lat}, {lon}).")
        else:
            print("No locations found in the database.")
    else:
        print("Configuration not loaded.")

if __name__ == "__main__":
    main()
