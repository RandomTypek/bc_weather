import requests
import csv
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

def main():
    api_key = 'API_KEY'

    with open('../data/stops_small.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        
        for row in reader:
            # Extract latitude and longitude from the row
            lat = float(row['Zemepisna sirka'].replace(',', '.'))
            lon = float(row['Zemepisna dlzka'].replace(',', '.'))

            # Skip if latitude or longitude is zero
            if lat == 0 or lon == 0:
                print(f"Ignoring row for bus stop {row['Nazov zastavky']}: Latitude or longitude is zero.")
                print()
                continue

            # Call the API
            weather_data = call_weather_api(lat, lon, api_key)

            # Print weather data if fetched successfully
            if weather_data:
                current_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                print(f"Weather data fetched successfully for bus stop {row['Obec']} {row['Nazov zastavky']} at {current_time}.")
                for key, value in weather_data.items():
                    if isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            print(f"{key}.{sub_key}: {sub_value}")
                    else:
                        print(f"{key}: {value}")
                print()  # Add an empty line for separation
            else:
                print(f"Failed to fetch weather forecast for bus stop {row['Nazov zastavky']}.")

if __name__ == "__main__":
    main()
