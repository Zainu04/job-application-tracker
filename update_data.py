
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

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
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()

    application_id = 1
    new_status = "Offer"

    query = """
        UPDATE applications
        SET status = %s
        WHERE application_id = %s
    """

    cursor.execute(query, (new_status, application_id))
    connection.commit()

    if cursor.rowcount > 0:
        print("Application successfully updated!")
        print(f"Application ID: {application_id}")
        print(f"New status: {new_status}")
        print(f"Rows updated: {cursor.rowcount}")
    else:
        print(f"No application found with ID {application_id}.")

except Error as error:
    if connection is not None:
        connection.rollback()

    print(f"Error updating application: {error}")

finally:
    if cursor is not None:
        cursor.close()

    if connection is not None and connection.is_connected():
        connection.close()
