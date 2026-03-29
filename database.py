"""MySQL connection for the Job Application Tracker."""

import os

import mysql.connector
from dotenv import load_dotenv

# Load variables from .env into the process environment
load_dotenv()


def get_db_config():
    return {
        "host": os.getenv("MYSQL_HOST"),
        "user": os.getenv("MYSQL_USER"),
        "password": os.getenv("MYSQL_PASSWORD"),
        "database": os.getenv("MYSQL_DATABASE"),
    }


def get_db():
    return mysql.connector.connect(**get_db_config())
