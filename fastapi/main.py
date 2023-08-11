from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from passlib.context import CryptContext
import subprocess
import re

# Retrieve DB_HOST value from Terraform output
DB_HOST = subprocess.check_output(["terraform", "output", "-raw", "instance_address"], cwd="C:\\Users\\Dell\\OneDrive - Northeastern University\\courses\\big data and intl analytics\\DAMG7245-Summer2023\\final_project\\pipeline\\terraform").decode().strip()

# Database Configuration
DB_USER = 'stackai'
DB_PASSWORD = 'hello123'
DB_NAME = 'stackai'
DB_PORT = '5432'  # Default PostgreSQL port 

# Set up database connection
engine = create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Set up password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Set up FastAPI app
app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Set up database models
class User(Base):
    __tablename__ = "stackiusers"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

# Create all tables in the database
Base.metadata.create_all(bind=engine)

# Set up Pydantic models
class UserIn(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    first_name: str
    last_name: str

# Utility functions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def validate_email(email: str):
    if not re.search(r"\.(com|edu)$", email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email must end with .com or .edu")
    if not re.search(r"@(gmail|yahoo|outlook)\.com$|@(northeastern)\.edu$", email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email must be from a supported provider (gmail.com, yahoo.com, outlook.com, or northeastern.edu)")

def validate_password(password: str):
    if len(password) < 8:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be at least 8 characters long")
    if not re.search(r"\d", password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must contain at least one digit")
    if not re.search(r"[A-Z]", password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must contain at least one uppercase letter")
    if not re.search(r"[a-z]", password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must contain at least one lowercase letter")

def authenticate_user(db, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

# API routes
@app.post("/signup", response_model=UserOut)
def signup(user_in: UserIn, db=Depends(get_db)):
    if not user_in.first_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="First name cannot be blank")
    if not user_in.last_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Last name cannot be blank")
    validate_email(user_in.email)
    validate_password(user_in.password)
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists, please login instead")
    user = User(first_name=user_in.first_name, last_name=user_in.last_name, email=user_in.email, hashed_password=get_password_hash(user_in.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"first_name": user.first_name, "last_name": user.last_name}


@app.post("/login", response_model=UserOut)
def login(form_data: OAuth2PasswordRequestForm=Depends(), db=Depends(get_db)):
    if not form_data.username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email cannot be blank")
    if not form_data.password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password cannot be blank")
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect email or password",
                            headers={"WWW-Authenticate": "Bearer"})
    return {"first_name": user.first_name, "last_name": user.last_name}


# @app.get("/users/{username}", response_model=UserOut)
# def get_user(username: str, db=Depends(get_db)):
#     user = db.query(User).filter(User.username == username).first()
#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
#     return {"username": user.username, "hashed_password": user.hashed_password}

#get health
@app.get("/health")
def health():
    return {"status": "ok"}