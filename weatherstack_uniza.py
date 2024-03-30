import requests
import pandas as pd
from datetime import datetime

def call_weather_api(params):
    api_result = requests.get('http://api.weatherstack.com/current', params)
    api_response = api_result.json()
    return api_response

def parse_weather_data(data):
    if data is None:
        return None
    df = pd.DataFrame(data['current'])
    return df

def main():
    params = {
        'access_key': 'ACCESS_KEY',
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
