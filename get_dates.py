import csv
from datetime import datetime

def get_min_max_dates_from_csv(filename):
    with open(filename, 'r') as file:
        # Create a CSV reader object
        csv_reader = csv.reader(file, delimiter=';')

        # Read the header
        next(csv_reader)

        # Initialize variables to hold min and max dates
        min_date = datetime.max
        max_date = datetime.min

        # Iterate through rows to find min and max dates
        for row in csv_reader:
            date_str = row[1]  # Assuming 'Date' column is always at index 1
            date = datetime.strptime(date_str, '%y-%m-%d')

            if date < min_date:
                min_date = date

            if date > max_date:
                max_date = date

        return min_date.strftime('%y-%m-%d'), max_date.strftime('%y-%m-%d')
        
filename = 'data/data.csv'
min_date, max_date = get_min_max_dates_from_csv(filename)
print("Lowest (earliest) date:", min_date)
print("Highest (latest) date:", max_date)

