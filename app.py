"""
Job Application Tracker — JSON API + server-rendered UI shells (data via fetch).
SQL lives in queries.py; routes execute those statements here.
"""

from __future__ import annotations

import json
import os
import re
from datetime import date, datetime
from decimal import Decimal

from flask import Flask, jsonify, render_template, request
from mysql.connector import Error as MySQLError

from database import get_db
import queries as q

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-change-in-production")


def serialize_value(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat(timespec="seconds")
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (bytes, bytearray)):
        return value.decode("utf-8", errors="replace")
    return value


def serialize_row(row: dict | None) -> dict | None:
    if row is None:
        return None
    out = {}
    for key, val in row.items():
        if key in ("requirements", "interview_data") and val is not None:
            if isinstance(val, (dict, list)):
                out[key] = val
            elif isinstance(val, str):
                try:
                    out[key] = json.loads(val)
                except json.JSONDecodeError:
                    out[key] = val
            else:
                out[key] = serialize_value(val)
        else:
            out[key] = serialize_value(val)
    return out


def serialize_rows(rows: list) -> list:
    return [serialize_row(r) for r in rows]


def json_body():
    if not request.data:
        return {}
    try:
        return request.get_json(force=False, silent=False) or {}
    except Exception:
        return None


def to_mysql_json(value):
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return json.dumps(value)


def parse_job_requirements_as_skill_list(requirements) -> list[str]:
    """Normalize jobs.requirements JSON into a list of skill strings (lowercase)."""
    if requirements is None:
        return []
    data = requirements
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            return []

    skills: list[str] = []
    if isinstance(data, list):
        skills = [str(x).strip() for x in data if str(x).strip()]
    elif isinstance(data, dict):
        for key in ("skills", "must_have", "required", "requirements"):
            chunk = data.get(key)
            if isinstance(chunk, list):
                skills.extend(str(x).strip() for x in chunk if str(x).strip())
                break
        if not skills:
            skills = [str(k).strip() for k in data.keys() if str(k).strip()]
    return [s.lower() for s in skills if s]


def normalize_skill_token(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())


def compute_skill_match(user_skills: list[str], job_skill_list: list[str]) -> tuple[int, int, float]:
    """
    Returns (matched_count, user_skill_count, match_percent).
    Percent = matched / len(user_skills) * 100 when user_skills non-empty, else 0.
    """
    user = [normalize_skill_token(x) for x in user_skills if normalize_skill_token(x)]
    if not user:
        return 0, 0, 0.0
    job_set = set(job_skill_list)
    matched = sum(1 for us in user if us in job_set)
    pct = round(100.0 * matched / len(user), 1)
    return matched, len(user), pct


# --- Health -------------------------------------------------------------------


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


# --- Dashboard ----------------------------------------------------------------


@app.get("/api/dashboard/stats")
def dashboard_stats():
    conn = get_db()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(q.DASHBOARD_STATS)
        stats = cur.fetchone()
        cur.execute(q.APPLICATION_COUNTS_BY_STATUS)
        by_status = cur.fetchall()
        return jsonify(
            {
                "stats": serialize_row(stats),
                "applications_by_status": serialize_rows(by_status),
            }
        )
    except MySQLError as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


# --- Companies ----------------------------------------------------------------


@app.get("/api/companies")
def list_companies():
    conn = get_db()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(q.LIST_COMPANIES)
        return jsonify({"companies": serialize_rows(cur.fetchall())})
    except MySQLError as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


@app.get("/api/companies/<int:company_id>")
def get_company(company_id):
    conn = get_db()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(q.GET_COMPANY_BY_ID, (company_id,))
        row = cur.fetchone()
        if not row:
            return jsonify({"error": "Company not found"}), 404
        return jsonify({"company": serialize_row(row)})
    except MySQLError as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


@app.post("/api/companies")
def create_company():
    body = json_body()
    if body is None:
        return jsonify({"error": "Invalid JSON"}), 400
    name = body.get("company_name")
    if not name:
        return jsonify({"error": "company_name is required"}), 400
    conn = get_db()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            q.INSERT_COMPANY,
            (
                name,
                body.get("industry"),
                body.get("website"),
                body.get("city"),
                body.get("state"),
                body.get("notes"),
            ),
        )
        conn.commit()
        new_id = cur.lastrowid
        cur.execute(q.GET_COMPANY_BY_ID, (new_id,))
        row = cur.fetchone()
        return jsonify({"company": serialize_row(row)}), 201
    except MySQLError as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()


@app.put("/api/companies/<int:company_id>")
def update_company(company_id):
    body = json_body()
    if body is None:
        return jsonify({"error": "Invalid JSON"}), 400
    name = body.get("company_name")
    if not name:
        return jsonify({"error": "company_name is required"}), 400
    conn = get_db()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            q.UPDATE_COMPANY,
            (
                name,
                body.get("industry"),
                body.get("website"),
                body.get("city"),
                body.get("state"),
                body.get("notes"),
                company_id,
            ),
        )
        conn.commit()
        if cur.rowcount == 0:
            return jsonify({"error": "Company not found"}), 404
        cur.execute(q.GET_COMPANY_BY_ID, (company_id,))
        row = cur.fetchone()
        return jsonify({"company": serialize_row(row)})
    except MySQLError as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()


@app.delete("/api/companies/<int:company_id>")
def delete_company(company_id):
    conn = get_db()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(q.DELETE_COMPANY, (company_id,))
        conn.commit()
        if cur.rowcount == 0:
            return jsonify({"error": "Company not found"}), 404
        return jsonify({"deleted": True, "company_id": company_id})
    except MySQLError as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()


# --- Jobs ---------------------------------------------------------------------


@app.get("/api/jobs")
def list_jobs():
    detailed = request.args.get("detailed", "").lower() in ("1", "true", "yes")
    conn = get_db()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(q.LIST_JOBS_WITH_COMPANY if detailed else q.LIST_JOBS)
        return jsonify({"jobs": serialize_rows(cur.fetchall())})
    except MySQLError as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


@app.get("/api/jobs/<int:job_id>")
def get_job(job_id):
    detailed = request.args.get("detailed", "").lower() in ("1", "true", "yes")
    conn = get_db()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            q.GET_JOB_WITH_COMPANY_BY_ID if detailed else q.GET_JOB_BY_ID,
            (job_id,),
        )
        row = cur.fetchone()
        if not row:
            return jsonify({"error": "Job not found"}), 404
        return jsonify({"job": serialize_row(row)})
    except MySQLError as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


@app.post("/api/jobs")
def create_job():
    body = json_body()
    if body is None:
        return jsonify({"error": "Invalid JSON"}), 400
    company_id = body.get("company_id")
    title = body.get("job_title")
    if company_id is None or not title:
        return jsonify({"error": "company_id and job_title are required"}), 400
    conn = get_db()
    try:
        cur = conn.cursor(dictionary=True)
        is_active = 1 if body.get("is_active", True) else 0
        cur.execute(
            q.INSERT_JOB,
            (
                company_id,
                title,
                body.get("job_description"),
                body.get("salary_min"),
                body.get("salary_max"),
                body.get("job_type"),
                body.get("posting_url"),
                body.get("date_posted"),
                is_active,
                to_mysql_json(body.get("requirements")),
            ),
        )
        conn.commit()
        new_id = cur.lastrowid
        cur.execute(q.GET_JOB_BY_ID, (new_id,))
        row = cur.fetchone()
        return jsonify({"job": serialize_row(row)}), 201
    except MySQLError as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()


@app.put("/api/jobs/<int:job_id>")
def update_job(job_id):
    body = json_body()
    if body is None:
        return jsonify({"error": "Invalid JSON"}), 400
    company_id = body.get("company_id")
    title = body.get("job_title")
    if company_id is None or not title:
        return jsonify({"error": "company_id and job_title are required"}), 400
    conn = get_db()
    try:
        cur = conn.cursor(dictionary=True)
        is_active = 1 if body.get("is_active", True) else 0
        cur.execute(
            q.UPDATE_JOB,
            (
                company_id,
                title,
                body.get("job_description"),
                body.get("salary_min"),
                body.get("salary_max"),
                body.get("job_type"),
                body.get("posting_url"),
                body.get("date_posted"),
                is_active,
                to_mysql_json(body.get("requirements")),
                job_id,
            ),
        )
        conn.commit()
        if cur.rowcount == 0:
            return jsonify({"error": "Job not found"}), 404
        cur.execute(q.GET_JOB_BY_ID, (job_id,))
        row = cur.fetchone()
        return jsonify({"job": serialize_row(row)})
    except MySQLError as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()


@app.delete("/api/jobs/<int:job_id>")
def delete_job(job_id):
    conn = get_db()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(q.DELETE_JOB, (job_id,))
        conn.commit()
        if cur.rowcount == 0:
            return jsonify({"error": "Job not found"}), 404
        return jsonify({"deleted": True, "job_id": job_id})
    except MySQLError as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()


# --- Applications -------------------------------------------------------------


@app.get("/api/applications")
def list_applications():
    detailed = request.args.get("detailed", "").lower() in ("1", "true", "yes")
    conn = get_db()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            q.LIST_APPLICATIONS_WITH_DETAILS if detailed else q.LIST_APPLICATIONS
        )
        return jsonify({"applications": serialize_rows(cur.fetchall())})
    except MySQLError as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


@app.get("/api/applications/<int:application_id>")
def get_application(application_id):
    detailed = request.args.get("detailed", "").lower() in ("1", "true", "yes")
    conn = get_db()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            q.GET_APPLICATION_WITH_DETAILS_BY_ID if detailed else q.GET_APPLICATION_BY_ID,
            (application_id,),
        )
        row = cur.fetchone()
        if not row:
            return jsonify({"error": "Application not found"}), 404
        return jsonify({"application": serialize_row(row)})
    except MySQLError as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


@app.post("/api/applications")
def create_application():
    body = json_body()
    if body is None:
        return jsonify({"error": "Invalid JSON"}), 400
    job_id = body.get("job_id")
    app_date = body.get("application_date")
    if job_id is None or not app_date:
        return jsonify({"error": "job_id and application_date are required"}), 400
    conn = get_db()
    try:
        cur = conn.cursor(dictionary=True)
        cover = 1 if body.get("cover_letter_sent") else 0
        cur.execute(
            q.INSERT_APPLICATION,
            (
                job_id,
                app_date,
                body.get("status") or "Applied",
                body.get("resume_version"),
                cover,
                body.get("response_date"),
                body.get("interview_date"),
                body.get("notes"),
                to_mysql_json(body.get("interview_data")),
            ),
        )
        conn.commit()
        new_id = cur.lastrowid
        cur.execute(q.GET_APPLICATION_BY_ID, (new_id,))
        row = cur.fetchone()
        return jsonify({"application": serialize_row(row)}), 201
    except MySQLError as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()


@app.put("/api/applications/<int:application_id>")
def update_application(application_id):
    body = json_body()
    if body is None:
        return jsonify({"error": "Invalid JSON"}), 400
    job_id = body.get("job_id")
    app_date = body.get("application_date")
    if job_id is None or not app_date:
        return jsonify({"error": "job_id and application_date are required"}), 400
    conn = get_db()
    try:
        cur = conn.cursor(dictionary=True)
        cover = 1 if body.get("cover_letter_sent") else 0
        cur.execute(
            q.UPDATE_APPLICATION,
            (
                job_id,
                app_date,
                body.get("status") or "Applied",
                body.get("resume_version"),
                cover,
                body.get("response_date"),
                body.get("interview_date"),
                body.get("notes"),
                to_mysql_json(body.get("interview_data")),
                application_id,
            ),
        )
        conn.commit()
        if cur.rowcount == 0:
            return jsonify({"error": "Application not found"}), 404
        cur.execute(q.GET_APPLICATION_BY_ID, (application_id,))
        row = cur.fetchone()
        return jsonify({"application": serialize_row(row)})
    except MySQLError as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()


@app.delete("/api/applications/<int:application_id>")
def delete_application(application_id):
    conn = get_db()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(q.DELETE_APPLICATION, (application_id,))
        conn.commit()
        if cur.rowcount == 0:
            return jsonify({"error": "Application not found"}), 404
        return jsonify({"deleted": True, "application_id": application_id})
    except MySQLError as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()


# --- Contacts -----------------------------------------------------------------


@app.get("/api/contacts")
def list_contacts():
    detailed = request.args.get("detailed", "").lower() in ("1", "true", "yes")
    conn = get_db()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(q.LIST_CONTACTS_WITH_COMPANY if detailed else q.LIST_CONTACTS)
        return jsonify({"contacts": serialize_rows(cur.fetchall())})
    except MySQLError as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


@app.get("/api/contacts/<int:contact_id>")
def get_contact(contact_id):
    detailed = request.args.get("detailed", "").lower() in ("1", "true", "yes")
    conn = get_db()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            q.GET_CONTACT_WITH_COMPANY_BY_ID if detailed else q.GET_CONTACT_BY_ID,
            (contact_id,),
        )
        row = cur.fetchone()
        if not row:
            return jsonify({"error": "Contact not found"}), 404
        return jsonify({"contact": serialize_row(row)})
    except MySQLError as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


@app.post("/api/contacts")
def create_contact():
    body = json_body()
    if body is None:
        return jsonify({"error": "Invalid JSON"}), 400
    company_id = body.get("company_id")
    first = body.get("first_name")
    last = body.get("last_name")
    if company_id is None or not first or not last:
        return jsonify(
            {"error": "company_id, first_name, and last_name are required"}
        ), 400
    conn = get_db()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            q.INSERT_CONTACT,
            (
                company_id,
                first,
                last,
                body.get("email"),
                body.get("phone"),
                body.get("job_title"),
                body.get("linkedin_url"),
                body.get("notes"),
            ),
        )
        conn.commit()
        new_id = cur.lastrowid
        cur.execute(q.GET_CONTACT_BY_ID, (new_id,))
        row = cur.fetchone()
        return jsonify({"contact": serialize_row(row)}), 201
    except MySQLError as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()


@app.put("/api/contacts/<int:contact_id>")
def update_contact(contact_id):
    body = json_body()
    if body is None:
        return jsonify({"error": "Invalid JSON"}), 400
    company_id = body.get("company_id")
    first = body.get("first_name")
    last = body.get("last_name")
    if company_id is None or not first or not last:
        return jsonify(
            {"error": "company_id, first_name, and last_name are required"}
        ), 400
    conn = get_db()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            q.UPDATE_CONTACT,
            (
                company_id,
                first,
                last,
                body.get("email"),
                body.get("phone"),
                body.get("job_title"),
                body.get("linkedin_url"),
                body.get("notes"),
                contact_id,
            ),
        )
        conn.commit()
        if cur.rowcount == 0:
            return jsonify({"error": "Contact not found"}), 404
        cur.execute(q.GET_CONTACT_BY_ID, (contact_id,))
        row = cur.fetchone()
        return jsonify({"contact": serialize_row(row)})
    except MySQLError as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()


@app.delete("/api/contacts/<int:contact_id>")
def delete_contact(contact_id):
    conn = get_db()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(q.DELETE_CONTACT, (contact_id,))
        conn.commit()
        if cur.rowcount == 0:
            return jsonify({"error": "Contact not found"}), 404
        return jsonify({"deleted": True, "contact_id": contact_id})
    except MySQLError as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()


# --- Job match ----------------------------------------------------------------


@app.post("/api/job-match")
def job_match():
    body = json_body()
    if body is None:
        return jsonify({"error": "Invalid JSON"}), 400
    skills = body.get("skills")
    if not isinstance(skills, list) or not skills:
        return jsonify({"error": 'skills must be a non-empty array of strings'}), 400

    conn = get_db()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(q.JOBS_FOR_SKILL_MATCH)
        jobs = cur.fetchall()
    except MySQLError as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

    ranked = []
    for row in jobs:
        job_skills = parse_job_requirements_as_skill_list(row.get("requirements"))
        matched, total_user, pct = compute_skill_match(skills, job_skills)
        ranked.append(
            {
                "job_id": row["job_id"],
                "job_title": row["job_title"],
                "company_id": row["company_id"],
                "company_name": row["company_name"],
                "matched_skills": matched,
                "user_skills_count": total_user,
                "match_percent": pct,
                "job_requirements_parsed": job_skills,
            }
        )

    ranked.sort(key=lambda x: (-x["match_percent"], x["job_id"]))
    return jsonify({"matches": ranked})


# --- UI pages (plain HTML + JS fetch to /api) ---------------------------------


@app.get("/")
def page_dashboard():
    return render_template("dashboard.html")


@app.get("/companies")
def page_companies():
    return render_template("companies.html")


@app.get("/jobs")
def page_jobs():
    return render_template("jobs.html")


@app.get("/applications")
def page_applications():
    return render_template("applications.html")


@app.get("/contacts")
def page_contacts():
    return render_template("contacts.html")


@app.get("/job-match")
def page_job_match():
    return render_template("job_match.html")


if __name__ == "__main__":
    app.run(debug=True)
