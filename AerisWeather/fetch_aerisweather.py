import urllib
import json
import requests
import pandas as pd
import psycopg2
from datetime import datetime

try:
    with open('config.json') as config_file:
        config = json.load(config_file)
        
    client_id = config['client_id']
    client_secret = config['client_secret']
    location_data = config['location_data']
    dbname = config['dbname']
    user = config['user']
    password = config['password']
    host = config['host']
    
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host)
    
    # Call the API
    request = urllib.request.urlopen(f'https://api.aerisapi.com/conditions/49.201359,18.754791?format=json&plimit=1&filter=1min&client_id={client_id}&client_secret={client_secret}')
    response = request.read()
    
    # Check if response is empty
    if response:
        current_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        print(f"Weather data fetched successfully at {current_time}.")
        data = json.loads(response)
        request.close()
        pretty_json = json.dumps(data, indent=4)
        print(pretty_json)
    else:
        print("Error: Empty response from the API")
        
except psycopg2.Error as e:
    print(f"PostgreSQL Error: {e}")
except psycopg2.OperationalError as e:
    print(f"Error connecting to the PostgreSQL database: {e}")
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code} - {e.reason}")
except urllib.error.URLError as e:
    print(f"URL Error: {e.reason}")
except json.JSONDecodeError as e:
    print(f"JSON Decode Error: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
