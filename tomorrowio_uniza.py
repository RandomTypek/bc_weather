import requests
from datetime import datetime

def get_weather_forecast(location):
    api_key = 'YOUR_API_KEY'  # Replace 'YOUR_API_KEY' with your actual API key
    url = f'https://api.tomorrow.io/v4/weather/realtime?location={location}&apikey={api_key}'
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def display_forecast(response):
    if response:
        current_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        print(f"Weather data fetched successfully at {current_time}.")
        for key, value in response['data'].items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    print(f"{sub_key}: {sub_value}")
            else:
                print(f"{key}: {value}")
    else:
        print("Failed to fetch weather forecast.")

if __name__ == "__main__":
    location = "49.201359, 18.754791"
    forecast_data = get_weather_forecast(location)
    display_forecast(forecast_data)

