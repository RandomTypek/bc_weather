import csv
import psycopg2
from psycopg2 import sql
from datetime import datetime

def connect_to_database():
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            dbname="your_db_name",
            user="your_username",
            password="your_password",
            host="localhost"
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
        print(f"Error creating table: {e}")

def fill_table(conn):
    try:
        # Open the CSV file
        with open('../data/stops.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')

            # Insert data into the table
            with conn.cursor() as cursor:
                for row in reader:
                    cursor.execute(
                        """
                        INSERT INTO Locations (stop_id, latitude, longitude, state, region, town, town_part, stop_name)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (int(row['Cislo zastavky']), float(row['Zemepisna sirka'].replace(',', '.')), float(row['Zemepisna dlzka'].replace(',', '.')), row['Stat'], row['Okres'], row['Obec'], row['Cast obce'], row['Nazov zastavky'])
                    )
            conn.commit()
            print("Data inserted into table 'Locations'")
    except (psycopg2.Error, FileNotFoundError) as e:
        print(f"Error filling table: {e}")

def main():
    conn = connect_to_database()
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
