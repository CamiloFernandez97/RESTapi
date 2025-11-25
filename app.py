from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
from pathlib import Path

#This is the path to the SQLite file
DB_PATH = Path("incidents.db")

app = FLASK(__name__)


#This function opens the connection to the database

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row 
    return conn 


#This function initialize the table of the DB for the first time 
def init_db():
    if not DB_PATH.exist():
        conn = get_conn()
        cur = conn.cursos()

        #This creates the incident table
        cur.execute(" " "
            CREATE TABLE incidents(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                short_description TEXT NOT NULL,
                category TEXT,
                priority TEXT,
                status TEXT,
                assigned_to TEXT,
                created_at TEXT,
                updated_at TEXT
            );
     " " ")
    conn.commit()
    conn.close()


#This are the API routes

#This function checks if the api is working
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status" : "ok", "service" : "mini-item-api"}), 200

#This function gets all incidents from the database
@app.route("/incidents", methods=["GET"])
def list_incidents():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM incidents ORDER BY created_at DESC;")
    rows = cur.fetchall()
    conn.close()

    incidents = [dict(row) for row in rows]
    return jsonify(incidents), 200

#This function gets an specific incident from the database
@app.route("/incidents/<int:incident_id>", methods=["GET"])
def get_incident(incident_id):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM incidents WHERE id = ?;", (incident_id))
    row = cur.fetchone()
    conn.close()

    if row is None:
        return jsonify({"error": "Incident not found"}), 404
    return jsonify(dict(row)), 200

#This function post, creates a new ITSM incident
@app.route("/incidents", methods=["POST"])
def create_incident():
    data = request.get_json() or {}

    

