import requests
from datetime import datetime

def get_weather_data(api_key, latitude, longitude):
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
    if weather_data and 'data' in weather_data and len(weather_data['data']) > 0:
        current_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        print(f"Weather data fetched successfully at {current_time}.")
        for key, value in weather_data['data'][0].items():
            print(f"{key}: {value}")
    else:
        print("No weather data available.")

def main():
    # Replace 'API_KEY' with your actual API key from Weatherbit.io
    api_key = 'API_KEY'
    latitude = 49.201359
    longitude = 18.754791

    weather_data = get_weather_data(api_key, latitude, longitude)
    display_weather_data(weather_data)

if __name__ == "__main__":
    main()
