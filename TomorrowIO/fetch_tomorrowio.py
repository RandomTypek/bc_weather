import requests
import json
import psycopg2
from datetime import datetime

def get_weather_forecast(latitude, longitude, config):
    """
    Function to fetch weather forecast data from Tomorrow.io API.

    Args:
        latitude (float): Latitude of the location.
        longitude (float): Longitude of the location.
        config (dict): Configuration containing API key.

    Returns:
        dict: Weather forecast data in JSON format.
    """
    
    api_key = config['api_key']
    url = f'https://api.tomorrow.io/v4/weather/realtime?location={latitude},{longitude}&apikey={api_key}'
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
        
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Error: Unexpected status code {response.status_code}")
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

def display_forecast(response):
    """
    Function to display weather forecast data.

    Args:
        response (dict): Weather forecast data in JSON format.
    """
    
    if response and 'data' in response:
        current_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        print(f"Weather data fetched successfully at {current_time}.")
        for key, value in response['data'].items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    print(f"{sub_key}: {sub_value}")
            else:
                print(f"{key}: {value}")
        print()        
    else:
        print("Failed to fetch weather forecast.")

if __name__ == "__main__":
    try:
        with open('config.json') as config_file:
            config = json.load(config_file) # Loading configuration from JSON file
        
        connection = psycopg2.connect(
            dbname=config['dbname'],
            user=config['user'],
            password=config['password'],
            host=config['host']
        ) # Establishing connection to PostgreSQL database
            
        cursor = connection.cursor()
        cursor.execute("SELECT latitude, longitude FROM Locations")
        locations = cursor.fetchall()
        for location in locations:
            latitude, longitude = location
            
            # Ignore rows with zero latitude or longitude
            if latitude == 0 or longitude == 0:
                print(f"Ignoring row: Latitude or longitude is zero.")
                continue
                
            forecast_data = get_weather_forecast(latitude, longitude, config)
            display_forecast(forecast_data)
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
    finally:
        if connection:
            cursor.close()
            connection.close()
