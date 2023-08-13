import streamlit as st

from datetime import timedelta
from datetime import datetime
import requests
import pandas as pd

# Check if user is logged in and session is still valid
if "logged_in" in st.session_state and "last_activity" in st.session_state:
    time_since_last_activity = datetime.now() - st.session_state.last_activity
    if time_since_last_activity < timedelta(minutes=15):
        # Session is still valid, update last activity time
        st.session_state.last_activity = datetime.now()

        # Display logout button
        if st.sidebar.button("Logout"):
            del st.session_state.logged_in
            del st.session_state.last_activity
            #rerun the page
            st.experimental_rerun()

        st.markdown("""
        <style>
            .center {
                display: block;
                margin-left: auto;
                margin-right: auto;
                text-align: center;
            }
        </style>
        """, unsafe_allow_html=True)

        st.markdown("<h1 class='center'>StackAI Generated Answers</h1>", unsafe_allow_html=True)

        # Check if the result is stored in session state
        if "similar_topics" in st.session_state and "similarity_scores" in st.session_state:
            # Get the user input from session state
            user_input = st.session_state.user_question
            # Get the result from session state
            similar_topics = st.session_state.similar_topics
            similarity_scores = st.session_state.similarity_scores
            
            # Get the df2 DataFrame from session state
            df2 = st.session_state.df2
            
            # Filter out topics that do not have accepted answers
            similar_topics_with_accepted_answers = [topic for topic in similar_topics if topic['accepted_answer'] != 'N/A']

            # Filter out topics that have accepted answers
            unanswered_topics = [topic for topic in similar_topics if topic['accepted_answer'] == 'N/A']

            # Display the result
            if len(unanswered_topics) > 0:
                options = [f"{i+1}. {unanswered_topics[i]['question_title']} (similarity score: {similarity_scores[i]:.2f})" for i in range(len(unanswered_topics))]
                st.markdown("<h3> Unanswered Similar Topics :</h3>", unsafe_allow_html=True)
                selected_option = st.selectbox("", options)
            else:
                st.markdown("<h3> No Unanswered Similar Topics Found.</h3>", unsafe_allow_html=True)

            
            with st.spinner("Loading..."):
                # Add a button to display the AI answer of the selected topic
                if st.button("StackAI answer for similar topics"):

                    fastapi_url = "http://localhost:8000/generate_answer"

                    # Get the index of the selected topic
                    selected_index = options.index(selected_option)
                    
                    # Get the details of the selected topic
                    selected_topic = similar_topics_with_accepted_answers[selected_index]
                    question_id, question_title, question_body = selected_topic['question_id'], selected_topic['question_title'], selected_topic['question_body']
                    
                    # Create the data JSON payload
                    data = {
                        "question_title": str(question_title),
                        "question_body": str(question_body),
                        "temperature": 0.2  # Set the desired temperature here
                    }
                                        
                                    # Make a POST request to the FastAPI endpoint
                    response = requests.post(fastapi_url, json=data)

                    # Make a POST request to the FastAPI endpoint
                    try:
                        response = requests.post(fastapi_url, json=data)
                        response.raise_for_status()  # Raise an exception for non-200 status codes
                        if response.status_code == 200:
                            answer = response.json()["answer"]
                            st.markdown(f"<h4 style='color:green'>StackAI:</h4> {answer}", unsafe_allow_html=True)
                        else:
                            st.error("Failed to generate the answer. Please try again.")
                    except requests.exceptions.RequestException as e:
                        st.error(f"An error occurred while making the request: {e}")

                #openai answer to user question
                user_input = st.session_state.user_question
                # Display the user's question and the value of the user_input variable on the same line
                st.markdown(f"<h3>User's question : <span style='color:green'>{user_input}</span></h3>", unsafe_allow_html=True)
                with st.spinner("Loading..."):
                    if st.button("StackAI answer for user's question"):
                        # Get the model's response based on the user input and the given data
                        answer = get_openai_response_cached(user_input)

                        # Display the generated answer
                        st.markdown(f"<h4 style='color:green'>StackAI :</h4> {answer}", unsafe_allow_html=True)

        else:
            st.write("No result found. Please go back to first page and generate the result.")
    
    else:
        # Session has timed out, log out user and display login page
        del st.session_state.logged_in
        del st.session_state.last_activity
        
        # Display message asking user to log in
        st.warning("Please Sign In first")
        
else:
    # User is not logged in, display message asking user to log in and display login page
    st.warning("Please Sign In first")   
