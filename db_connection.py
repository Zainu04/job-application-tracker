
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

# Load database credentials from .env
load_dotenv()

config = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD"),
    "database": "pursuit_tracker"
}

connection = None
cursor = None

try:
    # Connect to MySQL
    connection = mysql.connector.connect(**config)

    if connection.is_connected():
        print("Successfully connected to MySQL!")
        print(f"Server version: {connection.get_server_info()}")

        # Get database information
        cursor = connection.cursor()
        cursor.execute("SELECT DATABASE();")

        database_name = cursor.fetchone()[0]
        print(f"Connected to database: {database_name}")

except Error as error:
    print(f"Error connecting to MySQL: {error}")

finally:
    if cursor is not None:
        cursor.close()

    if connection is not None and connection.is_connected():
        connection.close()
        print("Connection closed.")
