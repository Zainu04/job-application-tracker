
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

    query = """
        INSERT INTO companies
        (company_name, industry, website, city, state)
        VALUES (%s, %s, %s, %s, %s)
    """

    company_data = (
        "Python Solutions LLC",
        "Software Development",
        "www.pythonsolutions.com",
        "Miami",
        "Florida"
    )

    cursor.execute(query, company_data)
    connection.commit()

    print("Company successfully added!")
    print(f"New company ID: {cursor.lastrowid}")

except Error as error:
    if connection is not None:
        connection.rollback()

    print(f"Error inserting company: {error}")

finally:
    if cursor is not None:
        cursor.close()

    if connection is not None and connection.is_connected():
        connection.close()
