import requests
import pandas as pd
from datetime import datetime

def call_weather_api(lat, lon, api_key):
    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch data from the API")
        return None

def parse_weather_data(data):
    if data is None:
        return None
    df = pd.DataFrame(data['current'])
    #df = pd.DataFrame(data['minutely'])
    #df = pd.DataFrame(data['hourly'])
    #df = pd.DataFrame(data['daily'])
    return df

def main():
    api_key = 'API_KEY'

    # Latitude and longitude for the location
    lat = 49.201359
    lon = 18.754791

    # Call the API
    weather_data = call_weather_api(lat, lon, api_key)

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
