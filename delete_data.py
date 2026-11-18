
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

    company_name = "Python Solutions LLC"

    # Find and display the company before deleting it
    select_query = """
        SELECT company_id, company_name, industry, city
        FROM companies
        WHERE company_name = %s
    """

    cursor.execute(select_query, (company_name,))
    company = cursor.fetchone()

    if company:
        print("Company found:")
        print(company)

        delete_query = """
            DELETE FROM companies
            WHERE company_name = %s
        """

        cursor.execute(delete_query, (company_name,))
        connection.commit()

        print(f"Successfully deleted {cursor.rowcount} company record(s).")

    else:
        print("Company not found.")

except Error as error:
    if connection is not None:
        connection.rollback()

    print(f"Error deleting company: {error}")

finally:
    if cursor is not None:
        cursor.close()

    if connection is not None and connection.is_connected():
        connection.close()
