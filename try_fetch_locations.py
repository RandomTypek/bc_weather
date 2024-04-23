import requests
import csv

def get_coordinates(place_name):
    url = f"https://nominatim.openstreetmap.org/search?q={place_name}&format=json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data:
            return float(data[0]['lat']), float(data[0]['lon'])
    return None, None

def update_csv(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        next(reader)  # Skip header
        rows = list(reader)

    for row in rows:
        if row[1] == '0' and row[2] == '0':  # If lat lon are missing
            lat, lon = get_coordinates(row[5] + ", " + row[7].replace(',', '.'))
            if lat == None: #If precise location cannot be found, skip
                continue;
            print(f"Fetched missing coordinates for {row[5]}, {row[7]} - {lat}, {lon}")
            row[1] = str(lat)
            row[2] = str(lon)

    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['Cislo zastavky', 'Zemepisna sirka', 'Zemepisna dlzka', 'Stat', 'Okres', 'Obec', 'Cast obce', 'Nazov zastavky'])
        writer.writerows(rows)

if __name__ == "__main__":
    input_file = "data/stops.csv"
    output_file = "updated_bus_stops.csv"
    update_csv(input_file, output_file)
    print("CSV file updated successfully.")
