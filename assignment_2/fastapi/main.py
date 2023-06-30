from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import os
from dotenv import load_dotenv
from google.cloud.sql.connector import Connector
import sqlalchemy

load_dotenv()

app = FastAPI()
security = HTTPBasic()

# Set the environment variable
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/opt/airflow/dags/servicekey.json'

connector = Connector()

def getconn():
    conn = connector.connect(
        instance_connection_string="virtual-sylph-384316:us-west1:app",
        driver="pg8000",
        user="postgres",
        password="J1ag[@%$#1.@9k^^",
        db="postgres",
    )
    return conn

pool = sqlalchemy.create_engine("postgresql+pg8000://", creator=getconn).connect()

# Create users table
query = """
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    password TEXT NOT NULL
)
"""
pool.execute(query)

def validate_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    query = f"SELECT password FROM users WHERE username='{credentials.username}'"
    result = pool.execute(query).fetchone()
    if not result or credentials.password != result[0]:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return credentials.username

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/cloud-sql-status")
async def cloud_sql_status():
    try:
        pool.execute("SELECT 1")
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": f"Unable to connect to Cloud SQL: {e}"}


@app.post("/register")
async def register(username: str, password: str):
    query = f"INSERT INTO users (username, password) VALUES ('{username}', '{password}')"
    pool.execute(query)
    return {"message": f"User {username} registered successfully"}

@app.get("/login")
async def root(username: str = Depends(validate_credentials)):
    return {"message": f"Hello, {username}!"}