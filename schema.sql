-- =============================================================================
-- Job Application Tracker — database schema
-- =============================================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

CREATE DATABASE IF NOT EXISTS job_tracker
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE job_tracker;

DROP TABLE IF EXISTS applications;
DROP TABLE IF EXISTS contacts;
DROP TABLE IF EXISTS jobs;
DROP TABLE IF EXISTS companies;

SET FOREIGN_KEY_CHECKS = 1;

-- -----------------------------------------------------------------------------
-- companies
-- -----------------------------------------------------------------------------
CREATE TABLE companies (
  company_id INT NOT NULL AUTO_INCREMENT,
  company_name VARCHAR(100) NOT NULL,
  industry VARCHAR(50) DEFAULT NULL,
  website VARCHAR(200) DEFAULT NULL,
  city VARCHAR(50) DEFAULT NULL,
  state VARCHAR(50) DEFAULT NULL,
  notes TEXT,
  created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (company_id),
  KEY idx_company_industry (industry)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- jobs
-- -----------------------------------------------------------------------------
CREATE TABLE jobs (
  job_id INT NOT NULL AUTO_INCREMENT,
  company_id INT NOT NULL,
  job_title VARCHAR(100) NOT NULL,
  job_description TEXT,
  salary_min DECIMAL(10,2) DEFAULT NULL,
  salary_max DECIMAL(10,2) DEFAULT NULL,
  job_type VARCHAR(20) DEFAULT NULL,
  posting_url VARCHAR(500) DEFAULT NULL,
  date_posted DATE DEFAULT NULL,
  is_active TINYINT(1) DEFAULT 1,
  created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  requirements JSON DEFAULT NULL,
  PRIMARY KEY (job_id),
  KEY idx_job_title (job_title),
  KEY idx_company_type (company_id, job_type),
  CONSTRAINT fk_jobs_company
    FOREIGN KEY (company_id) REFERENCES companies (company_id)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- applications
-- -----------------------------------------------------------------------------
CREATE TABLE applications (
  application_id INT NOT NULL AUTO_INCREMENT,
  job_id INT NOT NULL,
  application_date DATE NOT NULL,
  status VARCHAR(30) DEFAULT 'Applied',
  resume_version VARCHAR(50) DEFAULT NULL,
  cover_letter_sent TINYINT(1) DEFAULT 0,
  response_date DATE DEFAULT NULL,
  interview_date DATETIME DEFAULT NULL,
  notes TEXT,
  created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  interview_data JSON DEFAULT NULL,
  PRIMARY KEY (application_id),
  KEY idx_app_status (status),
  CONSTRAINT fk_applications_job
    FOREIGN KEY (job_id) REFERENCES jobs (job_id)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- contacts
-- -----------------------------------------------------------------------------
CREATE TABLE contacts (
  contact_id INT NOT NULL AUTO_INCREMENT,
  company_id INT NOT NULL,
  first_name VARCHAR(50) NOT NULL,
  last_name VARCHAR(50) NOT NULL,
  email VARCHAR(100) DEFAULT NULL,
  phone VARCHAR(20) DEFAULT NULL,
  job_title VARCHAR(100) DEFAULT NULL,
  linkedin_url VARCHAR(200) DEFAULT NULL,
  notes TEXT,
  created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (contact_id),
  CONSTRAINT fk_contacts_company
    FOREIGN KEY (company_id) REFERENCES companies (company_id)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- Seed data
-- =============================================================================

INSERT INTO companies (company_name, industry, website, city, state) VALUES
('Tech Solutions Inc', 'Technology', 'www.techsolutions.com', 'Miami', 'Florida'),
('Data Analytics Corp', 'Data Science', 'www.dataanalytics.com', 'Austin', 'Texas'),
('Cloud Systems LLC', 'Cloud Computing', 'www.cloudsystems.com', 'Seattle', 'Washington'),
('Digital Innovations', 'Software', 'www.digitalinnovations.com', 'San Francisco', 'California'),
('Smart Tech Group', 'AI/ML', 'www.smarttech.com', 'Boston', 'Massachusetts');

INSERT INTO jobs (company_id, job_title, salary_min, salary_max, job_type, date_posted) VALUES
(1, 'Software Developer', 70000, 90000, 'Full-time', '2025-01-15'),
(1, 'Database Administrator', 75000, 95000, 'Full-time', '2025-01-10'),
(2, 'Data Analyst', 65000, 85000, 'Full-time', '2025-01-12'),
(3, 'Cloud Engineer', 80000, 100000, 'Full-time', '2025-01-08'),
(4, 'Junior Developer', 55000, 70000, 'Full-time', '2025-01-14'),
(4, 'Senior Developer', 95000, 120000, 'Full-time', '2025-01-14'),
(5, 'ML Engineer', 90000, 115000, 'Full-time', '2025-01-11');

INSERT INTO applications (job_id, application_date, status, resume_version, cover_letter_sent) VALUES
(1, '2025-01-16', 'Applied', 'v2.1', 1),
(3, '2025-01-13', 'Interview Scheduled', 'v2.1', 1),
(4, '2025-01-09', 'Rejected', 'v2.0', 0),
(5, '2025-01-15', 'Applied', 'v2.1', 1),
(7, '2025-01-12', 'Phone Screen', 'v2.1', 1);

INSERT INTO contacts (company_id, first_name, last_name, email, job_title) VALUES
(1, 'Sarah', 'Johnson', 'sjohnson@techsolutions.com', 'HR Manager'),
(2, 'Michael', 'Chen', 'mchen@dataanalytics.com', 'Technical Recruiter'),
(3, 'Emily', 'Williams', 'ewilliams@cloudsystems.com', 'Hiring Manager'),
(4, 'David', 'Brown', NULL, 'Senior Developer'),
(5, 'Lisa', 'Garcia', 'lgarcia@smarttech.com', 'Talent Acquisition');

-- =============================================================================
-- Seed data
-- =============================================================================

INSERT INTO jobs (company_id, job_title, salary_min, salary_max, job_type, date_posted) VALUES
(1, 'QA Engineer', 60000, 80000, 'Full-time', '2025-01-05'),
(2, 'Business Analyst', 65000, 85000, 'Full-time', '2025-01-06'),
(2, 'Data Scientist', 85000, 110000, 'Full-time', '2025-01-07'),
(3, 'DevOps Engineer', 80000, 105000, 'Full-time', '2025-01-08'),
(3, 'Security Analyst', 75000, 95000, 'Full-time', '2025-01-09'),
(4, 'UI/UX Designer', 60000, 80000, 'Full-time', '2025-01-10'),
(5, 'Product Manager', 90000, 120000, 'Full-time', '2025-01-11'),
(1, 'Technical Writer', 55000, 75000, 'Contract', '2025-01-12'),
(2, 'Intern - Data', 30000, 40000, 'Internship', '2025-01-13'),
(4, 'Intern - Development', 32000, 42000, 'Internship', '2025-01-14');
