import requests
from datetime import datetime

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

def main():
    api_key = 'API_KEY'

    # Latitude and longitude for the location
    lat = 49.201359
    lon = 18.754791

    # Call the API
    weather_data = call_weather_api(lat, lon, api_key)

    if weather_data:
        current_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        print(f"Weather data fetched successfully at {current_time}.")
        for key, value in weather_data.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    print(f"{key}.{sub_key}: {sub_value}")
            else:
                print(f"{key}: {value}")
    else:
        print("Failed to fetch weather forecast.")

if __name__ == "__main__":
    main()
