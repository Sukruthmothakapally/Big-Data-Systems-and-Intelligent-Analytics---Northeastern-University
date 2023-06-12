from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import os
import redis
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
security = HTTPBasic()

r = redis.Redis(
    host=os.getenv("DB_HOST", "localhost"),
    port=os.getenv("DB_PORT", "6379"),
    username=os.getenv("DB_USERNAME", ""),
    password=os.getenv("DB_PASSWORD", ""),
    decode_responses=True
)

def validate_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_password = r.get(f"user:{credentials.username}")
    if not correct_password or credentials.password != correct_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return credentials.username

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/redis-status")
async def redis_status():
    try:
        r.ping()
        return {"status": "ok"}
    except redis.exceptions.ConnectionError:
        return {"status": "error", "message": "Unable to connect to Redis"}


@app.post("/register")
async def register(username: str, password: str):
    r.set(f"user:{username}", password)
    return {"message": f"User {username} registered successfully"}

@app.get("/login")
async def root(username: str = Depends(validate_credentials)):
    return {"message": f"Hello, {username}!"}
