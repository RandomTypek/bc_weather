import csv
import json
import psycopg2

def load_config(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Config file '{filename}' not found.")
        return None
        
def create_database(config):
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user=config['user'],
            password=config['password'],
            host=config['host']
        )
        conn.autocommit = True
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 FROM pg_database WHERE datname='bcweather'")
            exists = cursor.fetchone()
            if not exists:
                cursor.execute("CREATE DATABASE bcweather")
                print("Database created successfully")
            else:
                print("Database already exists")
    except psycopg2.Error as e:
        print(f"Error creating or checking database: {e}")

def connect_to_database(config):
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            dbname=config['dbname'],
            user=config['user'],
            password=config['password'],
            host=config['host']
        )
        print("Connected to the database")
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        return None

def table_exists(conn):
    try:
        # Check if the table exists
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_name = 'Locations'
                )
                """
            )
            return cursor.fetchone()[0]
    except psycopg2.Error as e:
        print(f"Error checking if table exists: {e}")
        return False

def create_table(conn):
    try:
        # Create the table
        with conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE Locations (
                    stop_id INT PRIMARY KEY,
                    latitude DECIMAL,
                    longitude DECIMAL,
                    state VARCHAR(3),
                    region VARCHAR(3),
                    town VARCHAR(100),
                    town_part VARCHAR(100),
                    stop_name VARCHAR(100)
                )
                """
            )
        conn.commit()
        print("Table 'Locations' created successfully")
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Error creating table: {e}")

def fill_table(conn):
    try:
        # Open the CSV file
        with open('../data/stops_small.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')

            # Get existing stops from the database
            existing_stops = set()
            with conn.cursor() as cursor:
                cursor.execute("SELECT stop_id FROM Locations")
                rows = cursor.fetchall()
                existing_stops.update(row[0] for row in rows)

            # Insert new stops into the table
            with conn.cursor() as cursor:
                for row in reader:
                    stop_id = int(row['Cislo zastavky'])
                    if stop_id not in existing_stops:
                        cursor.execute(
                            """
                            INSERT INTO Locations (stop_id, latitude, longitude, state, region, town, town_part, stop_name)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            """,
                            (stop_id, float(row['Zemepisna sirka'].replace(',', '.')), float(row['Zemepisna dlzka'].replace(',', '.')), row['Stat'], row['Okres'], row['Obec'], row['Cast obce'], row['Nazov zastavky'])
                        )
            conn.commit()
            print("Data inserted into table 'Locations'")
    except (psycopg2.Error, FileNotFoundError) as e:
        conn.rollback()
        print(f"Error filling table: {e}")

def main():
    config = load_config('config.json')
    if config is None:
        return

    create_database(config)
    conn = connect_to_database(config)
    
    if conn is not None:
        if table_exists(conn):
            fill_table(conn)
        else:
            create_table(conn)
            fill_table(conn)
        conn.close()
    else:
        print("Unable to connect to the database")

if __name__ == "__main__":
    main()

