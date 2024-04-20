import requests
import pandas as pd
from datetime import datetime

def call_weather_api(params):
    try:
        api_result = requests.get('http://api.weatherstack.com/current', params)
        api_result.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
        api_response = api_result.json()
        return api_response
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

def parse_weather_data(data):
    if data is None:
        return None
    try:
        df = pd.DataFrame(data['current'])
        return df
    except KeyError as e:
        print(f"KeyError: {e}")
        return None

def main():
    params = {
        'access_key': 'API_KEY',
        'query': '49.201359, 18.754791',
        'units': 'm'
    }
    
    # Call the API
    weather_data = call_weather_api(params)

    # Parse the response and save it to DataFrame
    df = parse_weather_data(weather_data)

    if df is not None:
        current_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        print(f"Weather data fetched successfully at {current_time}.")
        for index, row in df.iterrows():
            print(f"Index: {index}")
            for col in df.columns:
                print(f"{col}: {row[col]}")
            print()
    else:
        print("Failed to fetch weather data.")

if __name__ == "__main__":
    main()
