import csv

def find_most_common_stop_id(file_path):
    stop_id_count = {}
    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        csv_reader = csv.DictReader(csvfile, delimiter=';')
        for row in csv_reader:
            stop_id = row['StopId']
            if stop_id in stop_id_count:
                stop_id_count[stop_id] += 1
            else:
                stop_id_count[stop_id] = 1
    most_common_stop_id = max(stop_id_count, key=stop_id_count.get)
    return most_common_stop_id

def get_stop_info(file_path, stop_id):
    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        csv_reader = csv.DictReader(csvfile, delimiter=';')
        for row in csv_reader:
            if row['Cislo zastavky'] == stop_id:
                return row['Obec'], row['Nazov zastavky']
    return None, None

def main():
    trip_file_path = 'data/data.csv'
    stop_file_path = 'data/stops.csv'

    most_common_stop_id = find_most_common_stop_id(trip_file_path)
    obec, nazov_zastavky = get_stop_info(stop_file_path, most_common_stop_id)

    if obec and nazov_zastavky:
        print(f"The most common StopId is '{most_common_stop_id}' which corresponds to stop {obec}, {nazov_zastavky}.")
    else:
        print("No information found for the most common StopId.")

if __name__ == "__main__":
    main()
