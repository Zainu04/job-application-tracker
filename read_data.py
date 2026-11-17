
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
        SELECT company_id, company_name, industry, city
        FROM companies
    """

    cursor.execute(query)
    companies = cursor.fetchall()

    print(f"\nTotal companies: {len(companies)}")
    print("\nCOMPANY LIST")
    print("-" * 60)

    for company in companies:
        company_id, name, industry, city = company

        print(f"ID: {company_id}")
        print(f"Name: {name}")
        print(f"Industry: {industry or 'N/A'}")
        print(f"City: {city or 'N/A'}")
        print("-" * 60)

except Error as error:
    print(f"Error reading companies: {error}")

finally:
    if cursor is not None:
        cursor.close()

    if connection is not None and connection.is_connected():
        connection.close()
