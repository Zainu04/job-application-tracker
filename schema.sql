
-- Pursuit Job Application Tracker
-- Database: pursuit_tracker

CREATE DATABASE IF NOT EXISTS pursuit_tracker;
USE pursuit_tracker;

-- 1. Companies
CREATE TABLE companies (
    company_id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(100) NOT NULL,
    industry VARCHAR(50),
    website VARCHAR(200),
    city VARCHAR(50),
    state VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_company_industry (industry)
) ENGINE=InnoDB;

-- 2. Jobs
CREATE TABLE jobs (
    job_id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT,
    job_title VARCHAR(100) NOT NULL,
    job_type ENUM('Full-time', 'Part-time', 'Contract', 'Internship'),
    salary_min INT,
    salary_max INT,
    job_url VARCHAR(300),
    date_posted DATE,
    requirements JSON,
    job_description TEXT,
    posting_url VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_job_title (job_title),
    INDEX idx_salary_min (salary_min),
    INDEX idx_company_type (company_id, job_type),

    CONSTRAINT fk_jobs_company
        FOREIGN KEY (company_id)
        REFERENCES companies(company_id)
) ENGINE=InnoDB;

-- 3. Applications
CREATE TABLE applications (
    application_id INT AUTO_INCREMENT PRIMARY KEY,
    job_id INT,
    application_date DATE NOT NULL,
    status ENUM('Applied', 'Screening', 'Interview', 'Offer', 'Rejected', 'Withdrawn'),
    resume_version VARCHAR(50),
    cover_letter_sent BOOLEAN,
    interview_data JSON,
    response_date DATE,
    interview_date DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_app_status (status),

    CONSTRAINT fk_applications_job
        FOREIGN KEY (job_id)
        REFERENCES jobs(job_id)
) ENGINE=InnoDB;

-- 4. Contacts
CREATE TABLE contacts (
    contact_id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT,
    contact_name VARCHAR(100) NOT NULL,
    title VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    linkedin_url VARCHAR(200),
    notes TEXT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_contact_company (company_id),

    CONSTRAINT fk_contacts_company
        FOREIGN KEY (company_id)
        REFERENCES companies(company_id)
) ENGINE=InnoDB;
