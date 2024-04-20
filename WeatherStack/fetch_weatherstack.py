import requests
import pandas as pd
from datetime import datetime
import psycopg2
import json

def load_config(filename):
    """
    Loads configuration parameters from a JSON file.
    
    Parameters:
        filename (str): The name of the JSON configuration file.
        
    Returns:
        dict or None: A dictionary containing the configuration parameters, or None if the file is not found.
    """
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        # If the config file is not found, print an error message
        print(f"Config file '{filename}' not found.")
        # Flush stdout to ensure immediate output
        sys.stdout.flush()
        return None
        
def connect_to_database(config):
    """
    Establishes a connection to a PostgreSQL database.
    
    Parameters:
        config (dict): A dictionary containing database connection parameters (dbname, user, password, host).
        
    Returns:
        psycopg2.connection or None: A connection object if successful, otherwise None.
    """
    try:
        # Establish connection using provided database credentials
        conn = psycopg2.connect(
            dbname=config['dbname'],
            user=config['user'],
            password=config['password'],
            host=config['host']
        )
        print("Connected to the database")
        return conn
    except psycopg2.Error as e:
        # If connection fails, print the error message
        print(f"Error connecting to the database: {e}")
        sys.stdout.flush()
        return None

def fetch_location_data(connection):
    """
    Fetches latitude and longitude data from a PostgreSQL database.
    
    Parameters:
        connection (psycopg2.connection): A connection object to the database.
        
    Returns:
        list or None: A list of tuples containing latitude and longitude pairs, or None if an error occurs.
    """
    try:
        # Create a cursor to execute SQL queries
        cursor = connection.cursor()
        # Execute SQL query to select latitude and longitude from the Locations table
        cursor.execute("SELECT latitude, longitude FROM Locations")
        # Fetch all rows from the result set
        location_data = cursor.fetchall()
        # Close the cursor
        cursor.close()
        return location_data
    except (Exception, psycopg2.Error) as error:
        # If an error occurs during database interaction, print the error message
        print("Error while fetching data from PostgreSQL", error)
        return None

def call_weather_api(params, config):
    """
    Calls a weather API to fetch weather data.
    
    Parameters:
        params (dict): A dictionary containing parameters for the API request.
        config (dict): A dictionary containing configuration parameters for the API request (request_url).
        
    Returns:
        dict or None: A dictionary containing the API response data, or None if an error occurs.
    """
    try:
        # Make a GET request to the weather API using provided parameters
        api_result = requests.get(config['request_url'], params)
        # Raise an exception for 4xx and 5xx status codes
        api_result.raise_for_status()
        # Parse the JSON response
        api_response = api_result.json()
        return api_response
    except requests.exceptions.RequestException as e:
        # If an error occurs during the request, print the error message
        print(f"Error fetching data: {e}")
        return None
    except requests.exceptions.HTTPError as e:
        # If an HTTP error occurs, print the error message
        print(f"HTTP error occurred: {e}")
        return None
    except requests.exceptions.ConnectionError as e:
        # If a connection error occurs, print the error message
        print(f"Error connecting to the server: {e}")
        return None
    except requests.exceptions.Timeout as e:
        # If a timeout error occurs, print the error message
        print(f"Timeout error occurred: {e}")
        return None
    except requests.exceptions.TooManyRedirects as e:
        # If there are too many redirects, print the error message
        print(f"Too many redirects: {e}")
        return None
    except ValueError as e:
        # If there's an error decoding JSON, print the error message
        print(f"Error decoding JSON: {e}")
        return None

def parse_weather_data(data):
    """
    Parses weather data from the API response.
    
    Parameters:
        data (dict): A dictionary containing the API response data.
        
    Returns:
        pandas.DataFrame or None: A DataFrame containing parsed weather data, or None if an error occurs.
    """
    if data is None:
        return None
    try:
        # Create a pandas DataFrame from the 'current' section of the API response
        df = pd.DataFrame(data['current'])
        return df
    except KeyError as e:
        # If the 'current' key is not found in the response, print the error message
        print(f"KeyError: {e}")
        return None

def main():
    # Load configuration from a JSON file
    config = load_config('config.json')
    if config is None:
        return
        
    # Connect to the PostgreSQL database
    connection = connect_to_database(config)
    if connection is None:
        print("Failed to connect to database.")
        return

    # Fetch all stops from the database
    location_data = fetch_location_data(connection)
    if location_data is None:
        print("Failed to fetch location data from the database.")
        return

    # Iterate over location data
    for latitude, longitude in location_data:
        # Ignore rows with zero latitude or longitude
        if latitude == 0 or longitude == 0:
            print(f"Ignoring row: Latitude or longitude is zero.")
            continue
            
        # Construct parameters for the weather API request
        params = {
            'access_key': config.get('api_key'),
            'query': f'{latitude},{longitude}',
            'units': 'm'
        }
    
        # Call the weather API
        weather_data = call_weather_api(params, config)

        # Parse the response and save it to DataFrame
        df = parse_weather_data(weather_data)

        # Print weather data if successfully fetched
        if df is not None:
            current_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            print(f"Weather data fetched successfully at {current_time}.")
            for index, row in df.iterrows():
                print(f"Index: {index}")
                for col in df.columns:
                    print(f"{col}: {row[col]}")
                print()
        else:
            print(f"Failed to fetch weather data.")

if __name__ == "__main__":
    main()

