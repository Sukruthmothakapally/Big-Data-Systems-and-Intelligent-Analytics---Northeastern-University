from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine, Column, Integer, String, inspect
from sqlalchemy.orm import sessionmaker, declarative_base
from passlib.context import CryptContext
import subprocess
import re
from typing import List
from fastapi import Depends, HTTPException
from langchain.chains.summarize import load_summarize_chain
from langchain.llms.openai import OpenAI

# Retrieve DB_HOST value from Terraform output
DB_HOST = "34.94.157.129"

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

# Define the User model
Base = declarative_base()
class User(Base):
    __tablename__ = "stackaiusers2"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

# Check if table already exists
inspector = inspect(engine)
if not inspector.has_table(table_name=User.__tablename__):
    # Create table if it does not exist
    User.__table__.create(bind=engine)

# Set up Pydantic models
class UserIn(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    first_name: str
    last_name: str

class UserWithEmailOut(BaseModel):
    first_name: str
    last_name: str
    email: str

# Define a class for the request body
class SummarizeRequest(BaseModel):
    data: str # The text to be summarized
    temperature: float # The temperature parameter for OpenAI
    chain_type: str # The chain type for OpenAI

# Define a class for the response body
class SummarizeResponse(BaseModel):
    summary: str # The summary of the text

class Document:
    def __init__(self, page_content):
        self.page_content = page_content
        self.metadata = {}

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

#get health
@app.get("/health")
def health():
    return {"status": "ok"}

# Define a function to initialize the OpenAI module and load the summarize chain
def init_openai_and_load_summarize_chain(openai_api_key, temperature, chain_type):
    # Initialize the OpenAI module
    llm = OpenAI(temperature=temperature, openai_api_key=openai_api_key)
    # Load the summarize chain
    chain = load_summarize_chain(llm, chain_type)
    return llm, chain

# Define a route for summarizing text using OpenAI
@app.post("/summarize", response_model=SummarizeResponse)
def summarize(request: SummarizeRequest):
    # Get the request parameters
    data = request.data
    temperature = request.temperature
    chain_type = request.chain_type

    # Create a Document object from the data string
    doc = Document(page_content=data)
    # Initialize the OpenAI module and load the summarize chain
    llm, chain = init_openai_and_load_summarize_chain(openai_api_key="xxxx", temperature=temperature, chain_type=chain_type)

    # Use the string variable as input to the summarization chain
    summary = chain.run(input_documents=[doc], question="Write a concise summary within 300 words.")

    # Return the summary as a response
    return SummarizeResponse(summary=summary)
