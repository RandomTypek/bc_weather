import json
import psycopg2
import requests
from datetime import datetime

def load_config(filename):
    """
    Load configuration settings from a JSON file.

    Args:
        filename (str): The path to the JSON configuration file.

    Returns:
        dict: Configuration settings.
    """
    
    try:
        with open(filename, 'r') as f:
            config = json.load(f)
            return config
    except FileNotFoundError:
        print(f"Config file '{filename}' not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON in '{filename}'.")
        return None
        
def connect_to_database(config):
    """
    Connect to the PostgreSQL database.

    Args:
        config (dict): Database connection parameters.

    Returns:
        psycopg2.connection: Connection object if successful, None otherwise.
    """
    
    try:
        connection = psycopg2.connect(
            dbname=config['dbname'],
            user=config['user'],
            password=config['password'],
            host=config['host']
        )
        return connection
    except psycopg2.Error as e:
        print(f"Unable to connect to the database: {e}")
        return None
        
def get_locations_from_database(connection):
    """
    Fetch locations (latitude, longitude) from the database.

    Args:
        connection (psycopg2.connection): Connection object to the database.

    Returns:
        list: List of tuples containing latitude and longitude of locations.
    """
    
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT latitude, longitude FROM Locations")
        locations = cursor.fetchall()
        return locations
    except psycopg2.Error as e:
        print(f"Error fetching locations from the database: {e}")
        return None        
        
def get_weather_data(api_key, latitude, longitude):
    """
    Get weather data from the Weatherbit API for a given latitude and longitude.

    Args:
        api_key (str): Weatherbit API key.
        latitude (float): Latitude of the location.
        longitude (float): Longitude of the location.

    Returns:
        dict: Weather data in JSON format.
    """
    
    try:
        url = f"https://api.weatherbit.io/v2.0/current?lat={latitude}&lon={longitude}&key={api_key}"
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print("Failed to retrieve data")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred: {e}")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"Error connecting to the server: {e}")
        return None
    except requests.exceptions.Timeout as e:
        print(f"Timeout error occurred: {e}")
        return None
    except requests.exceptions.TooManyRedirects as e:
        print(f"Too many redirects: {e}")
        return None
    except ValueError as e:
        print(f"Error decoding JSON: {e}")
        return None

def display_weather_data(weather_data):
    """
    Display weather data.

    Args:
        weather_data (dict): Weather data in JSON format.
    """
    
    if weather_data and 'data' in weather_data and len(weather_data['data']) > 0:
        current_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        print(f"Weather data fetched successfully at {current_time}.")
        for key, value in weather_data['data'][0].items():
            print(f"{key}: {value}")
    else:
        print("No weather data available.")

def main():
    config = load_config('config.json')
        
    if config:
        api_key = config['api_key']
        
        connection = connect_to_database(config)
        if connection:
            locations = get_locations_from_database(connection)
            if locations:
                for location in locations:
                    latitude, longitude = location
                     # Ignore rows with zero latitude or longitude
                    if latitude == 0 or longitude == 0:
                        print(f"Ignoring row: Latitude or longitude is zero.")
                        continue
                    weather_data = get_weather_data(api_key, latitude, longitude)
                    display_weather_data(weather_data)
            else:
                print("No locations found in the database.")
                connection.close()
        else:
            print("Unable to fetch weather data.")
    else:
        print("Configuration loading failed.")

if __name__ == "__main__":
    main()
