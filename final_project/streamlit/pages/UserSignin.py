from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
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

# Define the User model (table schema)
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(100), nullable=False)

# Create the table
Base.metadata.create_all(engine)

# Function to insert user data into the database
def store_user_data(username, email, password):
    new_user = User(username=username, email=email, password=password)
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
        user = session.query(User).filter_by(username=username, password=password).first()
        return user
    finally:
        session.close()

# Streamlit application
def main():
    st.title("Login Page")

    st.write("Sign In")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    sign_in_button = st.button("Sign In")

    st.write("Sign Up")
    new_username = st.text_input("New Username")
    new_email = st.text_input("Email", max_chars=100)  # Limit email input to 100 characters
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    sign_up_button = st.button("Sign Up")

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if sign_in_button:
        # Implement sign-in logic here using SQLAlchemy to query the database
        user = get_user(username, password)
        if user:
            st.experimental_set_query_params(authenticated=True)
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

    if "authenticated" in st.experimental_get_query_params():
        # Redirect to UserDashboard.py
        subprocess.run(["streamlit", "run", "UserDashboard.py"], check=True)
        # st.stop()  # Uncomment this line if you want to stop the current app after redirect

def user_dashboard():
    st.title("User Dashboard")
    st.write("Welcome to your dashboard!")

if __name__ == "__main__":
    main()