# #great expectations
# #details of all users (get method)
# #delete any user (delete method)
# import streamlit as st

# from datetime import timedelta
# from datetime import datetime
# import pandas as pd
# import requests

# # Replace this with the URL of your FastAPI backend
# FASTAPI_URL = "http://localhost:8000"

# # Set session timeout to 15 minutes
# SESSION_TIMEOUT = timedelta(minutes=15)

# # Helper function to make requests to FastAPI
# def make_request(url, method, headers=None, data=None):
#     if method == "get":
#         response = requests.get(url, headers=headers)
#     elif method == "delete":
#         response = requests.delete(url, headers=headers)
#     # Add other request methods as needed
#     return response

# # Check if user is logged in and session is still valid
# if "email" in st.session_state and "logged_in" in st.session_state and "last_activity" in st.session_state:
#     time_since_last_activity = datetime.now() - st.session_state.last_activity
#     if time_since_last_activity < timedelta(minutes=15):
#         # Session is still valid, update last activity time
#         st.session_state.last_activity = datetime.now()

#         # Display logout button
#         if st.sidebar.button("Logout"):
#             del st.session_state.logged_in
#             del st.session_state.last_activity
#             #rerun the page
#             st.experimental_rerun()
        
#         # Display welcome message with user's first name and last name
#         st.title(f"{st.session_state.first_name} {st.session_state.last_name}'s Admin Dashboard")

#         # View all users (admin-only)
#         if st.button("View All Users"):
#             response = make_request(f"{FASTAPI_URL}/users", "get")
#             if response.status_code == 200:
#                 users_data = response.json()
#                 st.write("User Details:")
#                 st.write(users_data)
#             else:
#                 st.error("Error fetching user details")

#         # Delete a user (admin-only)
#         if st.button("Delete User"):
#             user_to_delete = st.text_input("Enter the email of the user to delete")
#             if user_to_delete:
#                 response = make_request(f"{FASTAPI_URL}/users/{user_to_delete}", "delete")
#                 if response.status_code == 200:
#                     st.success(f"User {user_to_delete} has been deleted")
#                 else:
#                     st.error(f"Failed to delete user {user_to_delete}")
    
#     else:
#         # Session has timed out, log out user and display login page
#         del st.session_state.logged_in
#         del st.session_state.last_activity
        
#         # Display message asking user to log in
#         st.warning("Session timed out. Please Sign In again")
        
# else:
#     # User is not logged in, display message asking user to log in and display login page
#     st.warning("Only Admin can access this page. Please Sign In first")

import streamlit as st
import requests
from datetime import timedelta, datetime

# Replace this with the URL of your FastAPI backend
FASTAPI_URL = "http://fastapi:8095"

# Set session timeout to 15 minutes
SESSION_TIMEOUT = timedelta(minutes=15)

def admin_login():
    st.title("Admin Login")
    admin_email = st.text_input("Admin Email", key="admin_login_email")
    admin_password = st.text_input("Admin Password", type="password", key="admin_login_password")
    if st.button("Login as Admin"):
        if admin_email == "admin@gmail.com" and admin_password == "admin":
            st.session_state.admin_logged_in = True
            st.session_state.admin_email = admin_email
            st.success("Admin login successful")
        else:
            st.error("Invalid admin credentials")

def admin_dashboard():
    response = requests.get(f"{FASTAPI_URL}/get_all_users")
    if response.status_code == 200:
        user_data = response.json()

        st.title("Admin Dashboard - All Users")
        st.write("Here are all the registered users:")

        user_table = []
        for user in user_data:
            user_table.append([user["first_name"], user["last_name"], user["email"]])

        st.table(user_table)
    else:
        st.error("Failed to fetch user data")

# Main application
def main():
    # Check if admin is logged in
    if "admin_logged_in" not in st.session_state:
        admin_login()
    else:
        admin_dashboard()

if __name__ == "__main__":
    main()
