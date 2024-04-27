import requests
from datetime import datetime
import json
import time
import sys
import hopsworks
import pandas as pd
import uuid

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
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from file '{filename}': {e}")
        sys.stdout.flush()
        return None
        
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
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")
        sys.stdout.flush()
        return None

def process_weather_data(stop_data, api_key):
    """
    Process weather data for a given bus stop.

    Args:
        stop_data (dict): Dictionary containing bus stop data.
        api_key (str): API key for accessing the OpenWeatherMap API.

    Returns:
        dict: Processed weather data.
    """
    lat = stop_data['zemepisna_sirka']
    lon = stop_data['zemepisna_dlzka']
    town = stop_data['obec']
    stop_name = stop_data['nazov_zastavky']

    if lat == 0 or lon == 0:
        print(f"Ignoring row for bus stop {town}, {stop_name}: Latitude or longitude is zero.")
        return None

    weather_data = call_weather_api(lat, lon, api_key)
    if weather_data:
        try:
            relevant_data = {
                'weather_id': str(uuid.uuid4()),  # generate unique uuid
                'location_id': stop_data['cislo_zastavky'],
                'weather': weather_data['weather'],
                'main_temp': weather_data['main']['temp'],
                'main_feels_like': weather_data['main']['feels_like'],
                'main_temp_min': weather_data['main']['temp_min'],
                'main_temp_max': weather_data['main']['temp_max'],
                'main_pressure': weather_data['main']['pressure'],
                'main_humidity': weather_data['main']['humidity'],
                'main_sea_level': weather_data['main'].get('sea_level', 0),
                'main_grnd_level': weather_data['main'].get('grnd_level', 0),
                'visibility': weather_data.get('visibility', 0),
                'wind_speed': weather_data['wind']['speed'],
                'wind_deg': weather_data['wind']['deg'],
                'wind_gust': weather_data.get('wind').get('gust', 0),
                'clouds_all': weather_data['clouds']['all'],
                'rain_1h': weather_data.get('rain', {}).get('1h', 0),
                'rain_3h': weather_data.get('rain', {}).get('3h', 0),
                'snow_1h': weather_data.get('snow', {}).get('1h', 0),
                'snow_3h': weather_data.get('snow', {}).get('3h', 0),
                'dt': datetime.fromtimestamp(weather_data['dt']),
                'timestamp': datetime.now(),
                'sys_sunrise': datetime.fromtimestamp(weather_data['sys']['sunrise']),
                'sys_sunset': datetime.fromtimestamp(weather_data['sys']['sunset']),
                'timezone': weather_data['timezone']
            }
            print(f"Weather data for {town}, {stop_name} fetched successfully.")
            return relevant_data
        except KeyError as e:
            print(f"KeyError: {e}")
            sys.stdout.flush()
            return None
    else:
        print(f"Failed to fetch weather forecast for bus stop {town}, {stop_name}.")
        sys.stdout.flush()
        return None

def main():
    config = load_config('config.json')
    if config is None:
        return

    delay = config.get('delay', 3600)
    api_key = config.get('api_key')
    
    # login to Hopsworks
    project = hopsworks.login()
    
    # get feature store
    fs = project.get_feature_store(name='bc_weather_featurestore')
    
    # get feature view with stops
    feature_view_stops = fs.get_feature_view(
        name='stops_lat_lon',
        version=1
    )
    
    # get or create weather data feature group
    fg_weather = fs.get_or_create_feature_group(
        name="weather_data",
        version=1,
        description="Weather data for bus stops",
        primary_key=["weather_id"],
        online_enabled=True,
        event_time="timestamp",
    )
    
    try:
        while True:
            #get data from feature view, save to dataframe
            df_stops = feature_view_stops.get_batch_data()
            
            weather_data_list = []
            
            for index, row in df_stops.iterrows():
                stop_data = {
                    'cislo_zastavky': row['cislo_zastavky'],
                    'zemepisna_sirka': row['zemepisna_sirka'],
                    'zemepisna_dlzka': row['zemepisna_dlzka'],
                    'obec': row['obec'],
                    'nazov_zastavky': row['nazov_zastavky']
                }
                
                weather_data = process_weather_data(stop_data, api_key)
                if weather_data:
                    weather_data_list.append(weather_data)
            
            # create dataframe with weather data
            df_weather = pd.DataFrame(weather_data_list)
            
            fg_weather.insert(df_weather)
            
            print(f"Sleeping for {delay}s")            
            time.sleep(delay)               
    except Exception as e:
        print(f"Error: {e}")
        sys.stdout.flush()

if __name__ == "__main__":
    main()
