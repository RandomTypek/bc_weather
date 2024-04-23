import csv
import sys

def count_missing_coordinates(input_file):
    count = 0
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        next(reader)  # Skip header
        for row in reader:
            if row[1] == '0' and row[2] == '0':  # If lat lon are missing
                count += 1
    return count

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: count_missing.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    missing_count = count_missing_coordinates(input_file)
    print(f"Number of bus stops with missing coordinates in '{input_file}': {missing_count}")
