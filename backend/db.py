# db.py
import sqlite3

NDR_DB_NAME = "ndr_agent.db"
RESPONSE_DB_NAME = "responses.db"

def get_connection():
    return sqlite3.connect(NDR_DB_NAME)

def get_response_db_connection():
    return sqlite3.connect(RESPONSE_DB_NAME)
