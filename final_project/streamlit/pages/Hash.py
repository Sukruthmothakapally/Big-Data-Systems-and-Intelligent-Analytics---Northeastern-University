from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
import time
from jose import jwt
from datetime import datetime, timedelta
import streamlit as st
import subprocess

# Database Configuration
DB_USER = 'projectuser'
DB_PASSWORD = 'Ronaldo7'
DB_NAME = 'projectuser'
DB_HOST = '34.138.121.74'
DB_PORT = '5432'  # Default PostgreSQL port

engine = create_engine(f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')
Base = declarative_base()
Session = sessionmaker(bind=engine)

# Password Hashing Configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Access Token Configuration
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Define the User model (table schema)
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(200), nullable=False)

# Create the table
Base.metadata.create_all(engine)

# Function to hash the password
def hash_password(password):
    return pwd_context.hash(password)

# Function to insert user data into the database
def store_user_data(username, email, password):
    hashed_password = hash_password(password)
    new_user = User(username=username, email=email, password=hashed_password)
    session = Session()
    try:
        session.add(new_user)
        session.commit()
        return True
    except IntegrityError:
        session.rollback()
        return False
    finally:
        session.close()

# Function to retrieve user data from the database
def get_user(username, password):
    session = Session()
    try:
        user = session.query(User).filter_by(username=username).first()
        if user and verify_password(password, user.password):
            return user
    finally:
        session.close()
    return None

# Function to verify the password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Function to create access token
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Streamlit application
def main():
    st.title("Login Page")

    st.write("Sign In")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    sign_in_button = st.button("Sign In")

    st.write("Sign Up")
    new_username = st.text_input("New Username")
    new_email = st.text_input("Email")
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    sign_up_button = st.button("Sign Up")

    if sign_in_button:
        # Implement sign-in logic here using SQLAlchemy to query the database
        user = get_user(username, password)
        if user:
            # Issue an access token upon successful authentication
            access_token = create_access_token({"sub": user.username})
            st.session_state.access_token = access_token
            st.experimental_rerun()  # Rerun the Streamlit app to trigger the redirect
        else:
            st.error("Invalid username or password!")

    if sign_up_button:
        if new_password == confirm_password:
            # Store the new user data in the database using SQLAlchemy
            if store_user_data(new_username, new_email, new_password):
                st.success("Sign up successful! You can now sign in.")
            else:
                st.error("Username or email already exists!")
        else:
            st.error("Passwords do not match!")

    if "access_token" in st.session_state:
        subprocess.run(["streamlit", "run", "UserDashboard.py"], check=True)

def user_dashboard():
    st.title("User Dashboard")
    st.write("Welcome to your dashboard!")
    # Add your user dashboard content here

if __name__ == "__main__":
    main()
