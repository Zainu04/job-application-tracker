
import json
import os

from flask import (
    Flask, render_template, request, redirect, url_for, flash
)
from database import get_db_connection

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "pursuit-development-key")

APPLICATION_STATUSES = [
    "Applied",
    "Screening",
    "Interview",
    "Offer",
    "Rejected",
    "Withdrawn"
]


def fetch_all(query, params=()):
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


def execute_write(query, params=()):
    connection = get_db_connection()
    if connection is None:
        raise RuntimeError("Could not connect to the database.")

    cursor = connection.cursor()
    try:
        cursor.execute(query, params)
        connection.commit()
        return cursor.lastrowid
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def get_application_data():
    applications = fetch_all("""
        SELECT
            applications.*,
            jobs.job_title,
            companies.company_name
        FROM applications
        JOIN jobs ON applications.job_id = jobs.job_id
        JOIN companies ON jobs.company_id = companies.company_id
        ORDER BY applications.application_date DESC
    """)

    for application in applications:
        interview_data = application.get("interview_data")

        if isinstance(interview_data, str):
            try:
                interview_data = json.loads(interview_data)
            except (json.JSONDecodeError, TypeError):
                interview_data = {}

        if not isinstance(interview_data, dict):
            interview_data = {}

        application["follow_up_date"] = interview_data.get("follow_up_date", "")
        application["interview_notes"] = interview_data.get("notes", "")

    return applications


def get_form_interview_data():
    return json.dumps({
        "follow_up_date": request.form.get("follow_up_date", "").strip(),
        "notes": request.form.get("interview_notes", "").strip()
    })


# -------------------------
# DASHBOARD
# -------------------------

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
            "SELECT COUNT(*) AS total FROM applications "
            "WHERE status IN ('Screening', 'Interview')"
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


# -------------------------
# COMPANIES
# -------------------------

@app.route("/companies")
def companies():
    company_list = fetch_all("""
        SELECT
            companies.*,
            COUNT(jobs.job_id) AS job_count
        FROM companies
        LEFT JOIN jobs ON companies.company_id = jobs.company_id
        GROUP BY companies.company_id
        ORDER BY companies.company_name ASC
    """)

    return render_template(
        "companies.html",
        companies=company_list
    )


@app.route("/companies/add", methods=["POST"])
def add_company():
    company_name = request.form.get("company_name", "").strip()

    if not company_name:
        flash("Please enter a company name.", "error")
        return redirect(url_for("companies"))

    execute_write("""
        INSERT INTO companies (
            company_name,
            industry,
            website,
            city,
            state,
            notes
        )
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        company_name,
        request.form.get("industry", "").strip() or None,
        request.form.get("website", "").strip() or None,
        request.form.get("city", "").strip() or None,
        request.form.get("state", "").strip() or None,
        request.form.get("notes", "").strip() or None
    ))

    flash(f"{company_name} has been added.", "success")
    return redirect(url_for("companies"))


@app.route("/companies/<int:company_id>/edit", methods=["POST"])
def edit_company(company_id):
    company_name = request.form.get("company_name", "").strip()

    if not company_name:
        flash("Company name cannot be empty.", "error")
        return redirect(url_for("companies"))

    execute_write("""
        UPDATE companies
        SET company_name = %s,
            industry = %s,
            website = %s,
            city = %s,
            state = %s,
            notes = %s
        WHERE company_id = %s
    """, (
        company_name,
        request.form.get("industry", "").strip() or None,
        request.form.get("website", "").strip() or None,
        request.form.get("city", "").strip() or None,
        request.form.get("state", "").strip() or None,
        request.form.get("notes", "").strip() or None,
        company_id
    ))

    flash("Company information has been updated.", "success")
    return redirect(url_for("companies"))


@app.route("/companies/<int:company_id>/delete", methods=["POST"])
def delete_company(company_id):
    linked_jobs = fetch_one("""
        SELECT COUNT(*) AS total
        FROM jobs
        WHERE company_id = %s
    """, (company_id,))["total"]

    if linked_jobs > 0:
        flash(
            "This company has jobs linked to it. Delete or reassign those jobs first.",
            "error"
        )
        return redirect(url_for("companies"))

    execute_write(
        "DELETE FROM companies WHERE company_id = %s",
        (company_id,)
    )

    flash("Company has been deleted.", "success")
    return redirect(url_for("companies"))


# -------------------------
# JOBS
# -------------------------

@app.route("/jobs")
def jobs():
    job_list = fetch_all("""
        SELECT jobs.*, companies.company_name
        FROM jobs
        LEFT JOIN companies ON jobs.company_id = companies.company_id
        ORDER BY jobs.job_id DESC
    """)
    return render_template("jobs.html", jobs=job_list)


# -------------------------
# APPLICATIONS
# -------------------------

@app.route("/applications")
def applications():
    application_list = get_application_data()

    saved_jobs = fetch_all("""
        SELECT jobs.*, companies.company_name
        FROM jobs
        JOIN companies ON jobs.company_id = companies.company_id
        LEFT JOIN applications ON jobs.job_id = applications.job_id
        WHERE applications.application_id IS NULL
        ORDER BY jobs.job_id DESC
    """)

    job_options = fetch_all("""
        SELECT jobs.job_id, jobs.job_title, companies.company_name
        FROM jobs
        JOIN companies ON jobs.company_id = companies.company_id
        ORDER BY companies.company_name, jobs.job_title
    """)

    return render_template(
        "applications.html",
        applications=application_list,
        saved_jobs=saved_jobs,
        job_options=job_options,
        statuses=APPLICATION_STATUSES
    )


@app.route("/applications/add", methods=["POST"])
def add_application():
    job_id = request.form.get("job_id")
    application_date = request.form.get("application_date")
    status = request.form.get("status", "Applied")

    if not job_id or not application_date:
        flash("Please select a job and enter an application date.", "error")
        return redirect(url_for("applications"))

    if status not in APPLICATION_STATUSES:
        flash("Please select a valid application status.", "error")
        return redirect(url_for("applications"))

    execute_write("""
        INSERT INTO applications (
            job_id,
            application_date,
            status,
            resume_version,
            cover_letter_sent,
            interview_data
        )
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        job_id,
        application_date,
        status,
        request.form.get("resume_version", "").strip() or None,
        1 if request.form.get("cover_letter_sent") else 0,
        get_form_interview_data()
    ))

    flash("Your application has been added.", "success")
    return redirect(url_for("applications"))


@app.route("/applications/<int:application_id>/edit", methods=["POST"])
def edit_application(application_id):
    status = request.form.get("status")

    if status not in APPLICATION_STATUSES:
        flash("Please select a valid application status.", "error")
        return redirect(url_for("applications"))

    execute_write("""
        UPDATE applications
        SET application_date = %s,
            status = %s,
            resume_version = %s,
            cover_letter_sent = %s,
            interview_data = %s
        WHERE application_id = %s
    """, (
        request.form.get("application_date"),
        status,
        request.form.get("resume_version", "").strip() or None,
        1 if request.form.get("cover_letter_sent") else 0,
        get_form_interview_data(),
        application_id
    ))

    flash("Your application has been updated.", "success")
    return redirect(url_for("applications"))


@app.route("/applications/<int:application_id>/delete", methods=["POST"])
def delete_application(application_id):
    execute_write(
        "DELETE FROM applications WHERE application_id = %s",
        (application_id,)
    )

    flash("The application has been deleted.", "success")
    return redirect(url_for("applications"))


# -------------------------
# CONTACTS
# -------------------------

@app.route("/contacts")
def contacts():
    contact_list = fetch_all("""
        SELECT contacts.*, companies.company_name
        FROM contacts
        LEFT JOIN companies ON contacts.company_id = companies.company_id
        ORDER BY contacts.contact_name ASC
    """)
    return render_template("contacts.html", contacts=contact_list)


# -------------------------
# JOB MATCH
# -------------------------

@app.route("/job-match")
def job_match():
    return render_template("job_match.html", matches=[])


if __name__ == "__main__":
    app.run(debug=True)
