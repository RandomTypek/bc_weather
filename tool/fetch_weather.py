import requests
import psycopg2
from datetime import datetime

def connect_to_database():
    # Connect to the PostgreSQL database
    try:
        conn = psycopg2.connect(
            dbname="bcweather",
            user="your_username",
            password="your_password",
            host="localhost"
        )
        print("Connected to the database")
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        return None

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
    conn = connect_to_database()

    if conn is not None:
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM Locations")
                rows = cursor.fetchall()

                for row in rows:
                    # Extract latitude and longitude from the row
                    stop_id, lat, lon, _, _, _, _, stop_name = row

                    # Skip if latitude or longitude is zero
                    if lat == 0 or lon == 0:
                        print(f"Ignoring row for bus stop {stop_name}: Latitude or longitude is zero.")
                        continue

                    # Call the API
                    weather_data = call_weather_api(lat, lon, api_key)

                    # Print weather data if fetched successfully
                    if weather_data:
                        current_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                        print(f"Weather data fetched successfully for bus stop {stop_name} at {current_time}.")
                        for key, value in weather_data.items():
                            if isinstance(value, dict):
                                for sub_key, sub_value in value.items():
                                    print(f"{key}.{sub_key}: {sub_value}")
                            else:
                                print(f"{key}: {value}")
                        print()  # Add an empty line for separation
                    else:
                        print(f"Failed to fetch weather forecast for bus stop {stop_name}.")
        except psycopg2.Error as e:
            print(f"Error executing SQL query: {e}")
        finally:
            conn.close()
    else:
        print("Unable to connect to the database")

if __name__ == "__main__":
    main()
