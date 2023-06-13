import streamlit as st
import requests

api_url = "http://fastapi:8095" # Replace with your FastAPI URL

st.title("User Login")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):
    response = requests.get(f"{api_url}/login", auth=(username, password))
    if response.status_code == 200:
        st.session_state.username = username
        st.experimental_set_query_params(page="page2")
    else:
        st.error("Incorrect username or password")
