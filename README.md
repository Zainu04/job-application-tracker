
# Pursuit – Job Application Tracker

## Project Overview

Pursuit is a web-based Job Application Tracker developed for COP4751 – Advanced Database Management at Florida International University.

The application helps users organize and manage their job search by providing one centralized platform to track companies, job opportunities, applications, and professional contacts.

Built using Python, Flask, and MySQL, Pursuit demonstrates relational database design, database connectivity, CRUD operations, and dynamic web application development.

## Features

### 1. Dashboard
- Provides an overview of job search activity.
- Displays key statistics, including total applications and interview counts.
- Allows users to monitor application progress.
- Provides navigation to the application's main features.

### 2. Company Management
- Create new company records.
- View saved companies.
- Update existing company information.
- Delete company records when permitted by database relationships.
- Store company details, including name, industry, website, location, and notes.

### 3. Job Management
- Create job postings associated with companies.
- View available and saved job opportunities.
- Update job information.
- Delete job records.
- Store job titles, descriptions, salary ranges, job types, posting URLs, and posting dates.
- Track whether job postings are active.

### 4. Application Management
- Create applications associated with saved job opportunities.
- View and manage submitted applications.
- Update application statuses as the hiring process progresses.
- Delete application records.
- Track application dates, response dates, and interview dates.
- Record resume versions, cover letter information, and additional notes.

### 5. Contact Management
- Create professional contact records.
- Associate contacts with companies.
- View saved contact information.
- Update existing contacts.
- Delete contact records.
- Store contact names, job titles, email addresses, and additional information.

### 6. Job Match
- Evaluates job opportunities based on matching skills.
- Calculates a skill-match percentage for each job.
- Helps users identify opportunities that align with their skills.
- Provides a way to compare job opportunities based on skill compatibility.

### 7. User Interface
- Responsive website layout.
- Consistent navigation across application pages.
- Dashboard cards and organized data displays.
- Interactive forms and application controls.
- Subtle animations and visual transitions.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming language |
| Flask | Web application framework |
| MySQL | Relational database management system |
| MySQL Connector/Python | Database connectivity |
| HTML5 | Webpage structure |
| CSS3 | Styling and responsive design |
| JavaScript | Frontend interactions |
| Jinja2 | Dynamic HTML templating |

## Database Design

Pursuit uses a MySQL relational database named `pursuit_tracker`.

The database consists of four primary tables:

| Table | Description |
|---|---|
| `companies` | Stores company information. |
| `jobs` | Stores job postings associated with companies. |
| `applications` | Stores applications associated with job postings. |
| `contacts` | Stores professional contacts associated with companies. |

### Database Relationships

The database uses primary keys and foreign keys to maintain relationships between records.

- One company can have multiple job postings.
- One company can have multiple contacts.
- One job can have multiple application records.
- Applications reference existing jobs.
- Jobs and contacts reference their associated companies.

Foreign key constraints help maintain referential integrity and prevent invalid relationships between records.

The complete database structure is provided in `schema.sql`.

## Project Structure

```text
job-application-tracker/
│
├── app.py
├── database.py
├── schema.sql
├── requirements.txt
├── README.md
├── AI_USAGE.md
├── .env.example
├── .gitignore
│
├── static/
│   └── style.css
│
└── templates/
    ├── base.html
    ├── home.html
    ├── dashboard.html
    ├── companies.html
    ├── jobs.html
    ├── applications.html
    ├── contacts.html
    └── job_match.html
```

## Installation and Setup

Follow the instructions below to install and run Pursuit locally.

### Prerequisites

Before running the application, make sure you have installed:

- Python 3
- MySQL Server
- MySQL Workbench (recommended)
- Git

### 1. Clone the Repository

Clone the GitHub repository:

```bash
git clone https://github.com/Zainu04/job-application-tracker.git
```

Navigate into the project directory:

```bash
cd job-application-tracker
```

### 2. Create a Virtual Environment

Create a Python virtual environment:

```bash
python3 -m venv .venv
```

Activate the virtual environment on macOS or Linux:

```bash
source .venv/bin/activate
```

### 3. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### 4. Configure the MySQL Database

Make sure your MySQL server is running.

Open MySQL Workbench and execute the SQL statements in `schema.sql` to create the `pursuit_tracker` database and its tables.

The database must be created before running the Flask application.

### 5. Configure Environment Variables

Create a `.env` file in the root directory of the project.

Use `.env.example` as a reference and add your own MySQL connection credentials:

```env
DB_HOST=localhost
DB_USER=your_mysql_username
DB_PASSWORD=your_mysql_password
DB_NAME=pursuit_tracker
```

Replace the example values with your local MySQL credentials.

**Important:** The `.env` file contains private database credentials and should never be committed to GitHub.

### 6. Run the Flask Application

Start the application:

```bash
python app.py
```

Open your browser and navigate to:

```text
http://127.0.0.1:5000
```

The Pursuit Job Application Tracker should now be accessible locally.

## Project Requirements and Implementation

The project demonstrates the following database and application development concepts:

- Relational database creation and management.
- Primary keys and foreign key relationships.
- CRUD operations (Create, Read, Update, and Delete).
- Database connectivity using Python and MySQL Connector.
- Flask routes and server-side application logic.
- Dynamic HTML rendering using Jinja2.
- Form handling and user input validation.
- Referential integrity and relational database constraints.
- Dynamic job matching calculations.

## Generative AI Documentation

Generative AI tools were used as development assistance during the project.

The separate `AI_USAGE.md` file documents the use of these tools, including relevant prompts, generated suggestions or code, modifications made, and reflections on the development process.

## Project Demonstration

A project demonstration video will showcase the application's main features, database functionality, and user interface.

**Video Link:** [Insert project demonstration video link]

## Author

Developed for:

**COP4751 – Advanced Database Management**

Florida International University (FIU)

**Project:** Pursuit – Job Application Tracker
