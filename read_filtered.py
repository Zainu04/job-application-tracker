
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

    min_salary = 70000

    query = """
        SELECT job_title, salary_min, salary_max
        FROM jobs
        WHERE salary_min >= %s
    """

    cursor.execute(query, (min_salary,))
    jobs = cursor.fetchall()

    print(f"\nJobs with a minimum salary of ${min_salary:,} or more:")
    print("-" * 60)

    for job in jobs:
        job_title, salary_min, salary_max = job

        max_salary_display = (
            f"${salary_max:,}" if salary_max is not None else "N/A"
        )

        print(f"Job Title: {job_title}")
        print(f"Minimum Salary: ${salary_min:,}")
        print(f"Maximum Salary: {max_salary_display}")
        print("-" * 60)

    print(f"Total matching jobs: {len(jobs)}")

except Error as error:
    print(f"Error reading filtered jobs: {error}")

finally:
    if cursor is not None:
        cursor.close()

    if connection is not None and connection.is_connected():
        connection.close()
