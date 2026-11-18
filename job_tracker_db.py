
import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()


class JobTrackerDB:

    def __init__(self):
        self.config = {
            "host": os.getenv("DB_HOST", "localhost"),
            "user": os.getenv("DB_USER", "root"),
            "password": os.getenv("DB_PASSWORD"),
            "database": "pursuit_tracker"
        }
        self.connection = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(**self.config)

            if self.connection.is_connected():
                print("Successfully connected to Pursuit database!")
                return True

        except Error as e:
            print(f"Database connection error: {e}")
            return False

    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            self.connection = None
            print("Database connection closed.")

    def get_all_companies(self):
        try:
            cursor = self.connection.cursor(dictionary=True)

            query = "SELECT * FROM companies"
            cursor.execute(query)

            companies = cursor.fetchall()
            cursor.close()

            return companies

        except Error as e:
            print(f"Error retrieving companies: {e}")
            return []

    def get_jobs_by_salary(self, min_salary):
        try:
            cursor = self.connection.cursor(dictionary=True)

            query = """
                SELECT *
                FROM jobs
                WHERE salary_min >= %s
            """

            cursor.execute(query, (min_salary,))
            jobs = cursor.fetchall()
            cursor.close()

            return jobs

        except Error as e:
            print(f"Error retrieving jobs: {e}")
            return []

    def add_application(self, job_id, status="Applied"):
        cursor = None

        try:
            cursor = self.connection.cursor()

            query = """
                INSERT INTO applications
                (job_id, application_date, status)
                VALUES (%s, CURDATE(), %s)
            """

            cursor.execute(query, (job_id, status))
            self.connection.commit()

            application_id = cursor.lastrowid

            print(f"Application added successfully. ID: {application_id}")
            return application_id

        except Error as e:
            self.connection.rollback()
            print(f"Error adding application: {e}")
            return None

        finally:
            if cursor:
                cursor.close()


if __name__ == "__main__":

    db = JobTrackerDB()

    if db.connect():
        companies = db.get_all_companies()

        print(f"\nTotal companies: {len(companies)}")

        for company in companies:
            print(company["company_name"])

        db.disconnect()
