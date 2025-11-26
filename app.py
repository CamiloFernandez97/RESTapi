from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
from pathlib import Path

#This is the path to the SQLite file
DB_PATH = Path("incidents.db")

#app initialization statement 
app = FLASK(__name__)


#This function opens the connection to the database

def get_conn():
    #Initialize a variable with a connection instance to SQLite using the path assigned to incidents.db
    conn = sqlite3.connect(DB_PATH)
    #calls row object from the sqlite3 module
    conn.row_factory = sqlite3.Row 

    return conn 


#This function initialize the table of the DB for the first time 
def init_db():
    #Checks if the db instance exist
    if not DB_PATH.exists():
        #If instance does not exists then it initializes the connection variable with a a new conn call of the previous function
        conn = get_conn()
        #it assignes a cursor to the db connection to go through the data en in the DB
        cur = conn.cursor()
        #it executes an SQL script for the incidents table 
        cur.execute("""
            CREATE TABLE incidents(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                short_description TEXT NOT NULL,
                category TEXT,
                status TEXT,
                assigned_to TEXT,
                created_at TEXT,
                updated_at TEXT
                );
            """)
            #It commits the changes to the DB. 
            conn.commit()
            #It closes the outbound operations to the DB.  
            conn.close()

#=========== This are the API routes =====================

#This function checks if the api is working
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status" : "ok", "service" : "mini-item-api"}), 200

#This function gets all incidents from the database
@app.route("/incidents", methods=["GET"])
def list_incidents():
    ## Gets the connection to DB
    conn = get_conn()
    #Sets a cursor for DB connection management
    cur = conn.cursor()
    #Executes the SQL query 
    cur.execute("SELECT * FROM incidents ORDER BY created_at DESC;")
    #Fetches all rows from SQL tuple 
    rows = cur.fetchall()
    #Once all previous actions are executed it closes the connection to DB 
    conn.close()

    #Takes a variable and initialize it iterating the cursor over the incident tuple rows 
    incidents = [dict(row) for row in rows]
    #Converts the outcome of the previous iteration to json dictionary format. 
    return jsonify(incidents), 200




#This function gets an specific incident from the database
@app.route("/incidents/<int:incident_id>", methods=["GET"])
def get_incident(incident_id):
    #This initialize the variable conn with the connection object.
    conn = get_conn()
    #This assigns a cursor object to use in the connection tasks
    cur = conn.cursor()

    #This uses the cursor to perform a select all query in the data base entity by passing primary key as a parameter
    cur.execute("SELECT * FROM incidents WHERE id = ?;", (incident_id))
    #This assigns the fecthed element of the cursor query to variable row
    row = cur.fetchone()
    #Once the previous operations finish then object conn closes outbound and inbound connection to DB.
    conn.close()

    #This checks if row has a value assigned
    if row is None:
        #If no incidents found then it gives a not found 404.  
        return jsonify({"error": "Incident not found"}), 404
    #If there is an incident then it returns a JSON through the endpoint hence susccessful connection code 200
    return jsonify(dict(row)), 200


#This function post, creates a new ITSM incident
@app.route("/incidents", methods=["POST"])
def create_incident():
    #Here we assign a request containing an incident or an empty dictionary.
    data = request.get_json() or {}

    #Here we require a short description to be retrieve value from the request body.
    short_description = data.get("short description")
    #Here there is a conditional that checks if variable contains a value if not then send an error
    if not short_description:
        return jsonify({"error": "short_description is required"}), 400
    
    #Here I am assigning a default value to each variable. 
    category = data.get("category", "general")
    status = data.get("status", "open")
    priority  = data.get("priority", "P3")
    assigned_to = data.get("assigned_to", "unassigned")

    #this variable is recieving a date and time value in UTC format. 
    now = datetime.utcnow().isoformat()

    #Here we are opening a DB connection.
    conn = get_conn()
    cur = conn.cursor()


    #Here we are executing an SQL query of inserting values
    cur.execute("""
        INSERT INTO incidents(
            short_description, category, priority, status, assigned_to, created_at, updated_at
        )
        VALUES (?,?,?,?,?,?,?);
    """,(short_description, category, priority, status,
        assigned_to, now, now))
    
    #This will commit the changes to SQLite
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    #This will send the new value as a JSON message. 
    return jsonify({"id": new_id, "message": "Incident created"}), 201


#This function updates an incident 
@app.route("/incidents/<int:incident_id>", methods=["PUT"])
def update_incident(incident_id):

    data = request.get_json() or {}

    allowed_fields = ["Short_description", "category", "priority", "status", "assigned_to"]

    fields_to_update = {k: v for k, v in data.items() if k in allowed_fields}
    