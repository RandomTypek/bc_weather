import urllib
import json
import requests
import pandas as pd
from datetime import datetime

try:
    with open('config.json') as config_file:
        config = json.load(config_file)
        
    # Call the API
    request = urllib.request.urlopen(config['request_url'])
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

except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code} - {e.reason}")
except urllib.error.URLError as e:
    print(f"URL Error: {e.reason}")
except json.JSONDecodeError as e:
    print(f"JSON Decode Error: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
