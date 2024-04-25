import csv
import json
import hopsworks
import requests
import pandas as pd

def load_config(filename):
    """
    Load configuration settings from a JSON file.

    Args:
        filename (str): The path to the JSON configuration file.

    Returns:
        dict: Configuration settings.
    """
    
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Config file '{filename}' not found.")
        return None
        
def get_coordinates(place_name):
    """
    Get coordinates (latitude, longitude) for a given place name using OpenStreetMap API.

    Args:
        place_name (str): The name of the place to search for.

    Returns:
        tuple: A tuple containing latitude and longitude, or (0, 0) if not found.
    """
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={place_name}&format=json"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data:
                print(f"Fetched missing coordinates for '{place_name}'")
                return float(data[0]['lat']), float(data[0]['lon'])
    except Exception as e:
        print(f"Error retrieving coordinates for '{place_name}': {e}")
    return 0, 0

def main():
    config = load_config('config.json')
    if config is None:
        return

    project = hopsworks.login()
    fs = project.get_feature_store()
    
    #Define the file path to your CSV file
    file_path = config['location_data']

    # Define the delimiter used in your CSV file
    delimiter = ";"

    # Load the CSV file into a pandas DataFrame
    df = pd.read_csv(file_path, delimiter=delimiter, decimal=",", keep_default_na=False)
    
    # Check for missing coordinates and fetch if necessary
    for index, row in df.iterrows():
        if row['zemepisna_sirka'] == 0 and row['zemepisna_dlzka'] == 0:
            lat, lon = get_coordinates(row['obec'] + ", " + str(row['nazov_zastavky']).replace(',', '.'))
            df.at[index, 'zemepisna_sirka'] = lat
            df.at[index, 'zemepisna_dlzka'] = lon
    
    # Get or create the 'stops' feature group
    stops_fg = fs.get_or_create_feature_group(
        name="stops",
        version=1,
        description="Bus stop data",
        primary_key=["cislo_zastavky"],
        online_enabled=True,
    )
    
    # Insert data into feature group
    stops_fg.insert(df)

if __name__ == "__main__":
    main()

