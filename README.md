# Job Application Tracker

A full-stack web app for tracking job applications: companies, jobs, applications, contacts, a dashboard, and a skill-based job match view. The UI loads in the browser and talks to a Flask JSON API under `/api`.

## Stack

- **MySQL 8+** (database)
- **Python 3** with **Flask** (server, API, templates)
- **HTML / CSS / JavaScript** (interface; `fetch` to the API)

## Prerequisites

- [Python 3.10+](https://www.python.org/downloads/) (or similar)
- [MySQL Server](https://dev.mysql.com/downloads/mysql/) running locally (or reachable from your machine)
- A terminal and Git

## 1. Clone and enter the project

```bash
git clone https://github.com/jalvaradoas39/job-application-tracker.git
cd job-application-tracker
```

## 2. Create the database

Create schema, tables, indexes, and baseline seed data:

```bash
mysql -u root -p < schema.sql
```

Or open `schema.sql` in **MySQL Workbench**, select the full script, and execute it.

This creates the `job_tracker` database (if needed) and populates sample rows matching the COP4751 lab baseline.

## 3. Configure environment variables

In the project root, create a **`.env`** file (do not commit it). All of the following are **required** — the app reads them via `python-dotenv`:

```env
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=job_tracker
```

## 4. Python virtual environment and dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate    # For Windows use: .venv\Scripts\activate
pip install -r requirements.txt
```

## 5. Run the application

From the project root, with the virtual environment activated:

```bash
python3 app.py
```

Flask starts in debug mode on **port 5000** by default.

- **Web UI:** [http://127.0.0.1:5000](http://127.0.0.1:5000) (or `http://localhost:5000`)
- **JSON API:** same host, paths under `/api` (for example `/api/health`, `/api/companies`)

Stop the server with `Ctrl+C`.

## Project layout (high level)

| Path          | Role                                      |
| ------------- | ----------------------------------------- |
| `app.py`      | Flask app: page routes + `/api` endpoints |
| `database.py` | MySQL connection using `.env`             |
| `queries.py`  | Raw SQL used by the app                   |
| `schema.sql`  | Recreate DB + seed data                   |
| `templates/`  | HTML shells                               |
| `static/`     | CSS and JavaScript                        |

## Features

- Dashboard with counts and applications by status
- CRUD for companies, jobs, applications, and contacts
- Job match ranking from skills vs. each job’s `requirements` JSON (edit jobs in the UI to set JSON arrays such as `["Python","SQL"]`)
