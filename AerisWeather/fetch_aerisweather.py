import urllib
import json
import requests
import pandas as pd
import psycopg2
from datetime import datetime

try:
    # Load database and API configuration from a JSON file
    with open('config.json') as config_file:
        config = json.load(config_file)
        
    # Extract configuration parameters
    client_id = config['client_id']
    client_secret = config['client_secret']
    dbname = config['dbname']
    user = config['user']
    password = config['password']
    host = config['host']
    
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host)
    cursor = conn.cursor()
    
    # Retrieve latitude and longitude from the database
    cursor.execute("SELECT latitude, longitude FROM Locations")
    rows = cursor.fetchall()
    
    # Iterate over each row in the database
    for row in rows:
        latitude, longitude = row
        
        # Ignore rows with zero latitude or longitude
        if latitude == 0 or longitude == 0:
            print(f"Ignoring row: Latitude or longitude is zero.")
            continue
            
        # Fetch weather data from the Aeris Weather API
        request = urllib.request.urlopen(f'https://api.aerisapi.com/conditions/{latitude},{longitude}?format=json&plimit=1&filter=1min&client_id={client_id}&client_secret={client_secret}')
        response = request.read()

        # Check if response is empty
        if response:
            # Get the current time
            current_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            print(f"Weather data fetched successfully at {current_time} for latitude {latitude} and longitude {longitude}.")
            
            # Parse the JSON response
            data = json.loads(response)
            request.close()
            
            # Pretty print the JSON data
            pretty_json = json.dumps(data, indent=4)
            print(pretty_json)
            print()
        else:
            print(f"Error: Empty response from the API for latitude {latitude} and longitude {longitude}")

    # Close cursor and connection
    cursor.close()
    conn.close()

# Handle PostgreSQL errors
except psycopg2.Error as e:
    print(f"PostgreSQL Error: {e}")

# Handle connection errors
except psycopg2.OperationalError as e:
    print(f"Error connecting to the PostgreSQL database: {e}")

# Handle HTTP errors
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code} - {e.reason}")

# Handle URL errors
except urllib.error.URLError as e:
    print(f"URL Error: {e.reason}")

# Handle JSON decoding errors
except json.JSONDecodeError as e:
    print(f"JSON Decode Error: {e}")

# Handle other unexpected errors
except Exception as e:
    print(f"An error occurred: {e}")
