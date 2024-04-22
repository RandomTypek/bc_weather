import csv
import json
import psycopg2

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
        
def create_database(config):
    """
    Create the PostgreSQL database if it doesn't exist.

    Args:
        config (dict): Database connection parameters.
    """
    
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user=config['user'],
            password=config['password'],
            host=config['host']
        )
        conn.autocommit = True
        with conn.cursor() as cursor:
            # Check if the database exists
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
    """
    Connect to the PostgreSQL database.

    Args:
        config (dict): Database connection parameters.

    Returns:
        psycopg2.connection: Connection object if successful, None otherwise.
    """
    
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
    """
    Check if the 'Locations' table exists in the database.

    Args:
        conn (psycopg2.connection): Connection object to the PostgreSQL database.

    Returns:
        bool: True if the table exists, False otherwise.
    """
    
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
    """
    Create the 'Locations' table in the database.

    Args:
        conn (psycopg2.connection): Connection object to the PostgreSQL database.
    """
    
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

def fill_table(conn, config):
    """
    Fill the 'Locations' table with data from a CSV file.

    Args:
        conn (psycopg2.connection): Connection object to the PostgreSQL database.
        config (dict): Configuration settings.
    """
    
    try:
        # Open the CSV file
        with open(config['location_data'], newline='', encoding='utf-8') as csvfile:
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
            fill_table(conn, config)
        else:
            create_table(conn)
            fill_table(conn, config)
        conn.close()
    else:
        print("Unable to connect to the database")

if __name__ == "__main__":
    main()

