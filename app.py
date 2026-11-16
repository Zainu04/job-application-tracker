
from flask import Flask, render_template
from database import get_db_connection

app = Flask(__name__)


def fetch_all(query, params=()):
    """Execute a SELECT query and return all matching records."""
    connection = get_db_connection()

    if connection is None:
        raise RuntimeError("Could not connect to the database.")

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(query, params)
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


def fetch_one(query, params=()):
    """Execute a SELECT query and return one record."""
    connection = get_db_connection()

    if connection is None:
        raise RuntimeError("Could not connect to the database.")

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(query, params)
        return cursor.fetchone()
    finally:
        cursor.close()
        connection.close()


# Dashboard
@app.route("/")
def dashboard():
    stats = {
        "companies": fetch_one(
            "SELECT COUNT(*) AS total FROM companies"
        )["total"],
        "jobs": fetch_one(
            "SELECT COUNT(*) AS total FROM jobs"
        )["total"],
        "applications": fetch_one(
            "SELECT COUNT(*) AS total FROM applications"
        )["total"],
        "interviews": fetch_one(
            "SELECT COUNT(*) AS total FROM applications WHERE status = 'Interview'"
        )["total"]
    }

    recent_applications = fetch_all("""
        SELECT
            applications.application_id,
            companies.company_name,
            jobs.job_title,
            applications.application_date,
            applications.status
        FROM applications
        JOIN jobs ON applications.job_id = jobs.job_id
        JOIN companies ON jobs.company_id = companies.company_id
        ORDER BY applications.application_date DESC
        LIMIT 5
    """)

    return render_template(
        "dashboard.html",
        stats=stats,
        recent_applications=recent_applications
    )


# Companies
@app.route("/companies")
def companies():
    company_list = fetch_all("""
        SELECT * FROM companies
        ORDER BY company_name ASC
    """)

    return render_template(
        "companies.html",
        companies=company_list
    )


# Jobs
@app.route("/jobs")
def jobs():
    job_list = fetch_all("""
        SELECT
            jobs.*,
            companies.company_name
        FROM jobs
        LEFT JOIN companies ON jobs.company_id = companies.company_id
        ORDER BY jobs.job_id DESC
    """)

    return render_template(
        "jobs.html",
        jobs=job_list
    )


# Applications
@app.route("/applications")
def applications():
    application_list = fetch_all("""
        SELECT
            applications.*,
            jobs.job_title,
            companies.company_name
        FROM applications
        JOIN jobs ON applications.job_id = jobs.job_id
        JOIN companies ON jobs.company_id = companies.company_id
        ORDER BY applications.application_date DESC
    """)

    return render_template(
        "applications.html",
        applications=application_list
    )


# Contacts
@app.route("/contacts")
def contacts():
    contact_list = fetch_all("""
        SELECT
            contacts.*,
            companies.company_name
        FROM contacts
        LEFT JOIN companies ON contacts.company_id = companies.company_id
        ORDER BY contacts.contact_name ASC
    """)

    return render_template(
        "contacts.html",
        contacts=contact_list
    )


# Job Match
@app.route("/job-match")
def job_match():
    return render_template(
        "job_match.html",
        matches=[]
    )


if __name__ == "__main__":
    app.run(debug=True)
