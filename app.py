
import json
import os

from flask import Flask, render_template, request, redirect, url_for, flash
from database import get_db_connection

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "pursuit-development-key")

APPLICATION_STATUSES = [
    "Applied", "Screening", "Interview", "Offer", "Rejected", "Withdrawn"
]

JOB_TYPES = ["Full-time", "Part-time", "Contract", "Internship"]


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
        SELECT applications.*, jobs.job_title, companies.company_name
        FROM applications
        JOIN jobs ON applications.job_id = jobs.job_id
        JOIN companies ON jobs.company_id = companies.company_id
        ORDER BY applications.application_date DESC
    """)

    for application in applications:
        data = application.get("interview_data")

        if isinstance(data, str):
            try:
                data = json.loads(data)
            except (json.JSONDecodeError, TypeError):
                data = {}

        if not isinstance(data, dict):
            data = {}

        application["follow_up_date"] = data.get("follow_up_date", "")
        application["interview_notes"] = data.get("notes", "")

    return applications


def get_form_interview_data():
    return json.dumps({
        "follow_up_date": request.form.get("follow_up_date", "").strip(),
        "notes": request.form.get("interview_notes", "").strip()
    })


def get_job_requirements():
    """Convert comma-separated skills into a JSON list."""
    raw_skills = request.form.get("requirements", "")
    skills = [skill.strip() for skill in raw_skills.split(",") if skill.strip()]
    return json.dumps(skills)


def get_job_data():
    job_list = fetch_all("""
        SELECT jobs.*, companies.company_name
        FROM jobs
        LEFT JOIN companies ON jobs.company_id = companies.company_id
        ORDER BY jobs.job_id DESC
    """)

    for job in job_list:
        requirements = job.get("requirements")

        if isinstance(requirements, str):
            try:
                requirements = json.loads(requirements)
            except (json.JSONDecodeError, TypeError):
                requirements = []

        if isinstance(requirements, dict):
            requirements = list(requirements.keys())

        if not isinstance(requirements, list):
            requirements = []

        job["requirements_list"] = requirements
        job["requirements_text"] = ", ".join(str(skill) for skill in requirements)

    return job_list


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
        SELECT applications.application_id, companies.company_name,
               jobs.job_title, applications.application_date,
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
        SELECT companies.*, COUNT(jobs.job_id) AS job_count
        FROM companies
        LEFT JOIN jobs ON companies.company_id = jobs.company_id
        GROUP BY companies.company_id
        ORDER BY companies.company_name ASC
    """)
    return render_template("companies.html", companies=company_list)


@app.route("/companies/add", methods=["POST"])
def add_company():
    company_name = request.form.get("company_name", "").strip()

    if not company_name:
        flash("Please enter a company name.", "error")
        return redirect(url_for("companies"))

    execute_write("""
        INSERT INTO companies
            (company_name, industry, website, city, state, notes)
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
        SET company_name=%s, industry=%s, website=%s,
            city=%s, state=%s, notes=%s
        WHERE company_id=%s
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
    linked_jobs = fetch_one(
        "SELECT COUNT(*) AS total FROM jobs WHERE company_id=%s",
        (company_id,)
    )["total"]

    if linked_jobs:
        flash(
            "This company has jobs linked to it. Delete or reassign those jobs first.",
            "error"
        )
        return redirect(url_for("companies"))

    execute_write(
        "DELETE FROM companies WHERE company_id=%s",
        (company_id,)
    )
    flash("Company has been deleted.", "success")
    return redirect(url_for("companies"))


# -------------------------
# JOBS
# -------------------------

@app.route("/jobs")
def jobs():
    job_list = get_job_data()
    company_options = fetch_all(
        "SELECT company_id, company_name FROM companies ORDER BY company_name"
    )

    return render_template(
        "jobs.html",
        jobs=job_list,
        companies=company_options,
        job_types=JOB_TYPES
    )


@app.route("/jobs/add", methods=["POST"])
def add_job():
    company_id = request.form.get("company_id")
    job_title = request.form.get("job_title", "").strip()
    job_type = request.form.get("job_type") or None

    if not company_id or not job_title:
        flash("Please select a company and enter a job title.", "error")
        return redirect(url_for("jobs"))

    if job_type and job_type not in JOB_TYPES:
        flash("Please select a valid employment type.", "error")
        return redirect(url_for("jobs"))

    salary_min = request.form.get("salary_min", "").strip() or None
    salary_max = request.form.get("salary_max", "").strip() or None

    try:
        salary_min = int(salary_min) if salary_min is not None else None
        salary_max = int(salary_max) if salary_max is not None else None
    except ValueError:
        flash("Salary amounts must be whole numbers.", "error")
        return redirect(url_for("jobs"))

    if salary_min is not None and salary_max is not None and salary_min > salary_max:
        flash("Minimum salary cannot be greater than maximum salary.", "error")
        return redirect(url_for("jobs"))

    execute_write("""
        INSERT INTO jobs (
            company_id, job_title, job_type, salary_min, salary_max,
            job_url, date_posted, requirements
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        company_id,
        job_title,
        job_type,
        salary_min,
        salary_max,
        request.form.get("job_url", "").strip() or None,
        request.form.get("date_posted") or None,
        get_job_requirements()
    ))

    flash(f"{job_title} has been added to your jobs.", "success")
    return redirect(url_for("jobs"))


@app.route("/jobs/<int:job_id>/edit", methods=["POST"])
def edit_job(job_id):
    company_id = request.form.get("company_id")
    job_title = request.form.get("job_title", "").strip()
    job_type = request.form.get("job_type") or None

    if not company_id or not job_title:
        flash("Please select a company and enter a job title.", "error")
        return redirect(url_for("jobs"))

    if job_type and job_type not in JOB_TYPES:
        flash("Please select a valid employment type.", "error")
        return redirect(url_for("jobs"))

    salary_min = request.form.get("salary_min", "").strip() or None
    salary_max = request.form.get("salary_max", "").strip() or None

    try:
        salary_min = int(salary_min) if salary_min is not None else None
        salary_max = int(salary_max) if salary_max is not None else None
    except ValueError:
        flash("Salary amounts must be whole numbers.", "error")
        return redirect(url_for("jobs"))

    if salary_min is not None and salary_max is not None and salary_min > salary_max:
        flash("Minimum salary cannot be greater than maximum salary.", "error")
        return redirect(url_for("jobs"))

    execute_write("""
        UPDATE jobs
        SET company_id=%s, job_title=%s, job_type=%s,
            salary_min=%s, salary_max=%s, job_url=%s,
            date_posted=%s, requirements=%s
        WHERE job_id=%s
    """, (
        company_id,
        job_title,
        job_type,
        salary_min,
        salary_max,
        request.form.get("job_url", "").strip() or None,
        request.form.get("date_posted") or None,
        get_job_requirements(),
        job_id
    ))

    flash("Job information has been updated.", "success")
    return redirect(url_for("jobs"))


@app.route("/jobs/<int:job_id>/delete", methods=["POST"])
def delete_job(job_id):
    linked_applications = fetch_one(
        "SELECT COUNT(*) AS total FROM applications WHERE job_id=%s",
        (job_id,)
    )["total"]

    if linked_applications:
        flash(
            "This job has an application linked to it. Delete that application first.",
            "error"
        )
        return redirect(url_for("jobs"))

    execute_write("DELETE FROM jobs WHERE job_id=%s", (job_id,))
    flash("Job has been deleted.", "success")
    return redirect(url_for("jobs"))


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
            job_id, application_date, status, resume_version,
            cover_letter_sent, interview_data
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
        SET application_date=%s, status=%s, resume_version=%s,
            cover_letter_sent=%s, interview_data=%s
        WHERE application_id=%s
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
        "DELETE FROM applications WHERE application_id=%s",
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

    company_options = fetch_all("""
        SELECT company_id, company_name
        FROM companies
        ORDER BY company_name ASC
    """)

    return render_template(
        "contacts.html",
        contacts=contact_list,
        companies=company_options
    )


@app.route("/contacts/add", methods=["POST"])
def add_contact():
    contact_name = request.form.get("contact_name", "").strip()
    company_id = request.form.get("company_id")

    if not contact_name or not company_id:
        flash("Please enter a contact name and select a company.", "error")
        return redirect(url_for("contacts"))

    execute_write("""
        INSERT INTO contacts (
            company_id,
            contact_name,
            title,
            email,
            phone,
            linkedin_url,
            notes
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        company_id,
        contact_name,
        request.form.get("title", "").strip() or None,
        request.form.get("email", "").strip() or None,
        request.form.get("phone", "").strip() or None,
        request.form.get("linkedin_url", "").strip() or None,
        request.form.get("notes", "").strip() or None
    ))

    flash(f"{contact_name} has been added to your contacts.", "success")
    return redirect(url_for("contacts"))


@app.route("/contacts/<int:contact_id>/edit", methods=["POST"])
def edit_contact(contact_id):
    contact_name = request.form.get("contact_name", "").strip()
    company_id = request.form.get("company_id")

    if not contact_name or not company_id:
        flash("Please enter a contact name and select a company.", "error")
        return redirect(url_for("contacts"))

    execute_write("""
        UPDATE contacts
        SET company_id = %s,
            contact_name = %s,
            title = %s,
            email = %s,
            phone = %s,
            linkedin_url = %s,
            notes = %s
        WHERE contact_id = %s
    """, (
        company_id,
        contact_name,
        request.form.get("title", "").strip() or None,
        request.form.get("email", "").strip() or None,
        request.form.get("phone", "").strip() or None,
        request.form.get("linkedin_url", "").strip() or None,
        request.form.get("notes", "").strip() or None,
        contact_id
    ))

    flash("Contact information has been updated.", "success")
    return redirect(url_for("contacts"))


@app.route("/contacts/<int:contact_id>/delete", methods=["POST"])
def delete_contact(contact_id):
    execute_write(
        "DELETE FROM contacts WHERE contact_id = %s",
        (contact_id,)
    )

    flash("Contact has been deleted.", "success")
    return redirect(url_for("contacts"))



# -------------------------
# JOB MATCH
# -------------------------

@app.route("/job-match", methods=["GET", "POST"])
def job_match():
    matches = []
    user_skills = ""

    if request.method == "POST":
        user_skills = request.form.get("skills", "").strip()

        entered_skills = {
            skill.strip().lower()
            for skill in user_skills.split(",")
            if skill.strip()
        }

        jobs = get_job_data()

        for job in jobs:
            requirements = job.get("requirements_list", [])

            if not requirements:
                continue

            normalized_requirements = [
                skill.strip().lower()
                for skill in requirements
                if skill and skill.strip()
            ]

            if not normalized_requirements:
                continue

            matching_skills = [
                skill for skill in requirements
                if skill.strip().lower() in entered_skills
            ]

            missing_skills = [
                skill for skill in requirements
                if skill.strip().lower() not in entered_skills
            ]

            match_percentage = round(
                len(matching_skills) / len(normalized_requirements) * 100
            )

            job["matching_skills"] = matching_skills
            job["missing_skills"] = missing_skills
            job["match_percentage"] = match_percentage

            matches.append(job)

        matches.sort(
            key=lambda job: job["match_percentage"],
            reverse=True
        )

    return render_template(
        "job_match.html",
        matches=matches,
        user_skills=user_skills
    )

if __name__ == "__main__":
    app.run(debug=True)