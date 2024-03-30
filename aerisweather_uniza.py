import urllib
import json
import requests
import pandas as pd
from datetime import datetime

# Call the API
request = urllib.request.urlopen('https://api.aerisapi.com/conditions/49.201359,18.754791?format=json&plimit=1&filter=1min&client_id=CLIENT_ID&client_secret=CLIENT_SECRET')
response = request.read()
data = json.loads(response)
request.close()
pretty_json = json.dumps(data, indent=4)
print(pretty_json)
