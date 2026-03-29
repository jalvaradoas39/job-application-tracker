"""
Raw SQL for the Job Application Tracker.

Schema matches MySQL Workbench: companies, jobs, applications, contacts.
Use parameterized placeholders (%s) for all user-supplied values.
"""

# --- Dashboard & analytics ----------------------------------------------------

DASHBOARD_STATS = """
SELECT
    (SELECT COUNT(*) FROM companies) AS companies_count,
    (SELECT COUNT(*) FROM jobs) AS jobs_count,
    (SELECT COUNT(*) FROM jobs WHERE is_active = 1) AS active_jobs_count,
    (SELECT COUNT(*) FROM applications) AS applications_count,
    (SELECT COUNT(*) FROM contacts) AS contacts_count
"""

APPLICATION_COUNTS_BY_STATUS = """
SELECT status, COUNT(*) AS count
FROM applications
GROUP BY status
ORDER BY count DESC
"""

# --- Companies ----------------------------------------------------------------

LIST_COMPANIES = """
SELECT company_id, company_name, industry, website, city, state, notes, created_at
FROM companies
ORDER BY company_name
"""

GET_COMPANY_BY_ID = """
SELECT company_id, company_name, industry, website, city, state, notes, created_at
FROM companies
WHERE company_id = %s
"""

INSERT_COMPANY = """
INSERT INTO companies (company_name, industry, website, city, state, notes)
VALUES (%s, %s, %s, %s, %s, %s)
"""

UPDATE_COMPANY = """
UPDATE companies
SET company_name = %s,
    industry = %s,
    website = %s,
    city = %s,
    state = %s,
    notes = %s
WHERE company_id = %s
"""

DELETE_COMPANY = """
DELETE FROM companies
WHERE company_id = %s
"""

# --- Jobs ---------------------------------------------------------------------

LIST_JOBS = """
SELECT job_id, company_id, job_title, job_description, salary_min, salary_max,
       job_type, posting_url, date_posted, is_active, created_at, requirements
FROM jobs
ORDER BY date_posted DESC, job_id DESC
"""

LIST_JOBS_WITH_COMPANY = """
SELECT j.job_id, j.company_id, j.job_title, j.job_description,
       j.salary_min, j.salary_max, j.job_type, j.posting_url, j.date_posted,
       j.is_active, j.created_at, j.requirements,
       c.company_name, c.industry, c.city, c.state
FROM jobs j
INNER JOIN companies c ON j.company_id = c.company_id
ORDER BY j.date_posted DESC, j.job_id DESC
"""

GET_JOB_BY_ID = """
SELECT job_id, company_id, job_title, job_description, salary_min, salary_max,
       job_type, posting_url, date_posted, is_active, created_at, requirements
FROM jobs
WHERE job_id = %s
"""

GET_JOB_WITH_COMPANY_BY_ID = """
SELECT j.job_id, j.company_id, j.job_title, j.job_description,
       j.salary_min, j.salary_max, j.job_type, j.posting_url, j.date_posted,
       j.is_active, j.created_at, j.requirements,
       c.company_name, c.industry, c.city, c.state
FROM jobs j
INNER JOIN companies c ON j.company_id = c.company_id
WHERE j.job_id = %s
"""

INSERT_JOB = """
INSERT INTO jobs (
    company_id, job_title, job_description, salary_min, salary_max,
    job_type, posting_url, date_posted, is_active, requirements
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

UPDATE_JOB = """
UPDATE jobs
SET company_id = %s,
    job_title = %s,
    job_description = %s,
    salary_min = %s,
    salary_max = %s,
    job_type = %s,
    posting_url = %s,
    date_posted = %s,
    is_active = %s,
    requirements = %s
WHERE job_id = %s
"""

DELETE_JOB = """
DELETE FROM jobs
WHERE job_id = %s
"""

# --- Applications -------------------------------------------------------------

LIST_APPLICATIONS = """
SELECT application_id, job_id, application_date, status, resume_version,
       cover_letter_sent, response_date, interview_date, notes, created_at, interview_data
FROM applications
ORDER BY application_date DESC, application_id DESC
"""

LIST_APPLICATIONS_WITH_DETAILS = """
SELECT a.application_id, a.job_id, a.application_date, a.status, a.resume_version,
       a.cover_letter_sent, a.response_date, a.interview_date, a.notes,
       a.created_at, a.interview_data,
       j.job_title, j.company_id,
       c.company_name
FROM applications a
INNER JOIN jobs j ON a.job_id = j.job_id
INNER JOIN companies c ON j.company_id = c.company_id
ORDER BY a.application_date DESC, a.application_id DESC
"""

GET_APPLICATION_BY_ID = """
SELECT application_id, job_id, application_date, status, resume_version,
       cover_letter_sent, response_date, interview_date, notes, created_at, interview_data
FROM applications
WHERE application_id = %s
"""

GET_APPLICATION_WITH_DETAILS_BY_ID = """
SELECT a.application_id, a.job_id, a.application_date, a.status, a.resume_version,
       a.cover_letter_sent, a.response_date, a.interview_date, a.notes,
       a.created_at, a.interview_data,
       j.job_title, j.company_id,
       c.company_name
FROM applications a
INNER JOIN jobs j ON a.job_id = j.job_id
INNER JOIN companies c ON j.company_id = c.company_id
WHERE a.application_id = %s
"""

INSERT_APPLICATION = """
INSERT INTO applications (
    job_id, application_date, status, resume_version,
    cover_letter_sent, response_date, interview_date, notes, interview_data
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

UPDATE_APPLICATION = """
UPDATE applications
SET job_id = %s,
    application_date = %s,
    status = %s,
    resume_version = %s,
    cover_letter_sent = %s,
    response_date = %s,
    interview_date = %s,
    notes = %s,
    interview_data = %s
WHERE application_id = %s
"""

DELETE_APPLICATION = """
DELETE FROM applications
WHERE application_id = %s
"""

# --- Contacts -----------------------------------------------------------------

LIST_CONTACTS = """
SELECT contact_id, company_id, first_name, last_name, email, phone,
       job_title, linkedin_url, notes, created_at
FROM contacts
ORDER BY last_name, first_name
"""

LIST_CONTACTS_WITH_COMPANY = """
SELECT ct.contact_id, ct.company_id, ct.first_name, ct.last_name, ct.email, ct.phone,
       ct.job_title, ct.linkedin_url, ct.notes, ct.created_at,
       c.company_name
FROM contacts ct
INNER JOIN companies c ON ct.company_id = c.company_id
ORDER BY c.company_name, ct.last_name, ct.first_name
"""

GET_CONTACT_BY_ID = """
SELECT contact_id, company_id, first_name, last_name, email, phone,
       job_title, linkedin_url, notes, created_at
FROM contacts
WHERE contact_id = %s
"""

GET_CONTACT_WITH_COMPANY_BY_ID = """
SELECT ct.contact_id, ct.company_id, ct.first_name, ct.last_name, ct.email, ct.phone,
       ct.job_title, ct.linkedin_url, ct.notes, ct.created_at,
       c.company_name
FROM contacts ct
INNER JOIN companies c ON ct.company_id = c.company_id
WHERE ct.contact_id = %s
"""

INSERT_CONTACT = """
INSERT INTO contacts (
    company_id, first_name, last_name, email, phone, job_title, linkedin_url, notes
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""

UPDATE_CONTACT = """
UPDATE contacts
SET company_id = %s,
    first_name = %s,
    last_name = %s,
    email = %s,
    phone = %s,
    job_title = %s,
    linkedin_url = %s,
    notes = %s
WHERE contact_id = %s
"""

DELETE_CONTACT = """
DELETE FROM contacts
WHERE contact_id = %s
"""

# --- Job match (fetch jobs + requirements; match % computed in Python) --------

JOBS_FOR_SKILL_MATCH = """
SELECT j.job_id, j.job_title, j.requirements, j.company_id, c.company_name
FROM jobs j
INNER JOIN companies c ON j.company_id = c.company_id
WHERE j.is_active = 1
ORDER BY j.job_id
"""
