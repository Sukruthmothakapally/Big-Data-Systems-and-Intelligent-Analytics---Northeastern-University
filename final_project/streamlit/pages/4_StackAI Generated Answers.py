import streamlit as st

from datetime import timedelta
from datetime import datetime

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

        import openai
        import pandas as pd
        openai_api_key = "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"
        openai.api_key = openai_api_key

        # Define a function to get the OpenAI response and cache the result using st.cache
        @st.cache_data(show_spinner=False)
        def get_openai_response_cached(data):
            return get_openai_response(data)

        def get_openai_response(data):

            # Define the conversation history with system, user, and data messages
            conversation = f"You are a helpful assistant.\n\nData: {data}"

            # Use the OpenAI API to generate a response
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Give the answer to this question:"},
                    {"role": "system", "content": f"Data: {data}"}
                ],
                temperature=0.2,
                max_tokens=500
            )

            # Extract and return the model-generated answer from the response
            return response["choices"][0]["message"]["content"].strip()

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
            similarity_scores_with_accepted_answers = [similarity_scores[i] for i in range(len(similar_topics)) if similar_topics[i]['accepted_answer'] != 'N/A']

            # Display the result
            options = [f"{i+1}. {similar_topics_with_accepted_answers[i]['question_title']} (similarity score: {similarity_scores_with_accepted_answers[i]:.2f})" for i in range(len(similar_topics_with_accepted_answers))]
            st.markdown("<h3> Unanswered Similar Topics :</h3>", unsafe_allow_html=True)
            selected_option = st.selectbox("",options)
            
            with st.spinner("Loading..."):
                # Add a button to display the AI answer of the selected topic
                if st.button("StackAI answer for similar topics"):
                    # Get the index of the selected topic
                    selected_index = options.index(selected_option)
                    
                    # Get the details of the selected topic
                    selected_topic = similar_topics_with_accepted_answers[selected_index]
                    question_id, question_title, question_body, accepted_answer = selected_topic['question_id'], selected_topic['question_title'], selected_topic['question_body'], selected_topic['accepted_answer']
                    
                    # Define the data variable
                    data = f"{question_title}{question_body}{accepted_answer}"
                    
                    # Get the model's response based on the user input and the given data
                    answer = get_openai_response_cached(data)

                    # Display the generated answer
                    st.markdown(f"<h4 style='color:green'>StackAI :</h4> {answer}", unsafe_allow_html=True)

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
