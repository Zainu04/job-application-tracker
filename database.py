
import os
import mysql.connector
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME", "pursuit_tracker")
}


def get_db_connection():
    """Create and return a MySQL database connection."""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection

    except mysql.connector.Error as error:
        raise ConnectionError(
            f"Unable to connect to the Pursuit database: {error}"
        ) from error
