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

        st.markdown("<h1 class='center'>Topic Summarization</h1>", unsafe_allow_html=True)

        import pandas as pd
        from langchain.llms.openai import OpenAI
        from langchain.chains.summarize import load_summarize_chain
        #from scipy.spatial.distance import cdist
        import openai

        # Define a function to initialize the OpenAI module and load the summarize chain, and cache the result using st.cache
        @st.cache_data(show_spinner=False)
        def init_openai_and_load_summarize_chain(openai_api_key, temperature, chain_type):
            # Initialize the OpenAI module
            llm = OpenAI(temperature=temperature, openai_api_key=openai_api_key)
            # Load the summarize chain
            chain = load_summarize_chain(llm, chain_type)
            return llm, chain


        class Document:
            def __init__(self, page_content):
                self.page_content = page_content
                self.metadata = {}

        # Check if the result is stored in session state
        if "similar_topics" in st.session_state and "similarity_scores" in st.session_state:
            # Get the result from session state
            similar_topics = st.session_state.similar_topics
            similarity_scores = st.session_state.similarity_scores
            
            # Get the df2 DataFrame from session state
            df2 = st.session_state.df2

                # Create a form
            with st.form(key="my_form"):
                # Display the result
                options = [f"{i+1}. {similar_topics[i]['question_title']} (similarity score: {similarity_scores[i]:.2f})" for i in range(len(similar_topics))]
                st.markdown("<h3> Select a topic :</h3>", unsafe_allow_html=True)
                selected_option = st.selectbox("",options)

                    # Add radio buttons to display the details or summarize the selected topic
                radio_options = ["View details", "Summarize"]
                selected_radio = st.radio("", radio_options)

                # Add a submit button to process the selected option with loading spinner
                with st.spinner("Loading..."):
                    if st.form_submit_button("Submit"): 

                        if selected_radio == "View details":
                            # Get the index of the selected topic
                            selected_index = options.index(selected_option)
                            
                            # Get the details of the selected topic
                            selected_topic = similar_topics[selected_index]
                            question_id, question_title, question_body, accepted_answer = selected_topic['question_id'], selected_topic['question_title'], selected_topic['question_body'], selected_topic['accepted_answer']
                            
                            if (accepted_answer)=="N/A":
                                st.markdown("<h3 style='color:red'>No accepted answer</h3>", unsafe_allow_html=True)
                            else:
                                # Render the HTML content of the accepted answer
                                st.markdown(f"<h3 style='color:green'>Accepted answer:</h3> {accepted_answer}", unsafe_allow_html=True)

                                accepted_answer_creation_date = selected_topic['accepted_answer_creation_date']
                                accepted_answer_view_count = selected_topic['accepted_answer_view_count']
                                accepted_answer_score = selected_topic['accepted_answer_score']
                                owner_reputation = selected_topic['owner_reputation']
                                owner_badge = selected_topic['owner_badge']

                                # Set the color of the accepted answer view count based on its value
                                if accepted_answer_view_count > 1000:
                                    view_count_color = "green"
                                elif accepted_answer_view_count >= 500:
                                    view_count_color = "orange"
                                else:
                                    view_count_color = "red"

                                # Set the color of the accepted answer score based on its value
                                if accepted_answer_score > 5:
                                    score_color = "green"
                                elif accepted_answer_score >= 1:
                                    score_color = "orange"
                                else:
                                    score_color = "red"

                                # Set the color of the owner reputation based on its value
                                if owner_reputation > 1000:
                                    reputation_color = "green"
                                elif owner_reputation >= 500:
                                    reputation_color = "orange"
                                else:
                                    reputation_color = "red"

                                # Create an HTML table to display the details of the accepted answer
                                table_html = f"""
                                    <table>
                                        <tr>
                                            <th>Accepted answer creation date</th>
                                            <td>{accepted_answer_creation_date}</td>
                                        </tr>
                                        <tr>
                                            <th>Accepted answer view count</th>
                                            <td style="color: {view_count_color};">{accepted_answer_view_count}</td>
                                        </tr>
                                        <tr>
                                            <th>Accepted answer score</th>
                                            <td style="color: {score_color};">{accepted_answer_score}</td>
                                        </tr>
                                        <tr>
                                            <th>Owner reputation</th>
                                            <td style="color: {reputation_color};">{owner_reputation}</td>
                                        </tr>
                                        <tr>
                                            <th>Owner badge</th>
                                            <td>{owner_badge}</td>
                                        </tr>
                                    </table>
                                """
                                st.write(table_html, unsafe_allow_html=True)

                            post_comments = df2[df2['post_id'] == question_id]

                            st.markdown(f"<h3>Question body:{question_body}</h3>", unsafe_allow_html=True)

                            comments_text = ""
                            if not post_comments.empty:
                                st.markdown("<h3>Comments:</h3>", unsafe_allow_html=True)
                                for index, row in post_comments.iterrows():
                                    st.write(f"\t- {row['text']}")
                                    comments_text += f"\n- {row['text']}"
                                    comment_creation_date = row['creation_date']
                                    comment_score = row['score']

                                    # Set the color of the comment score based on its value
                                    if comment_score > 5:
                                        score_color = "green"
                                    elif comment_score >= 1:
                                        score_color = "orange"
                                    else:
                                        score_color = "red"

                                    # Create an HTML table to display the details of the comment
                                    table_html = f"""
                                        <table>
                                            <tr>
                                                <th>Comment creation date</th>
                                                <td>{comment_creation_date}</td>
                                            </tr>
                                            <tr>
                                                <th>Comment score</th>
                                                <td style="color: {score_color};">{comment_score}</td>
                                            </tr>
                                            
                                        </table>
                                    """
                                    st.write(table_html, unsafe_allow_html=True)


                            
                            #store accepted answer, comments, question_body, question_title in session state
                            st.session_state.accepted_answer = accepted_answer
                            st.session_state.comments_text = comments_text
                            st.session_state.question_body = question_body
                            st.session_state.question_title = question_title

                        elif selected_radio == "Summarize":

                            # Get the index of the selected topic
                            selected_index = options.index(selected_option)
                            # Get the details of the selected topic
                            selected_topic = similar_topics[selected_index]
                            question_id, question_title, question_body, accepted_answer = selected_topic['question_id'], selected_topic['question_title'], selected_topic['question_body'], selected_topic['accepted_answer']

                            # Get the details of the selected topic
                            data = f"{question_title}{question_body}{accepted_answer}"
                            # Create a Document object from the data string
                            doc = Document(page_content=data)
                            # Initialize the OpenAI module and load the summarize chain
                            llm, chain = init_openai_and_load_summarize_chain(openai_api_key="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", temperature=0, chain_type="stuff")

                            # Use the string variable as input to the summarization chain
                            summary = chain.run(input_documents=[doc], question="Write a concise summary within 300 words.")

                            # Store the summary in session state
                            st.session_state.summary = summary
                            # Display the summary
                            st.markdown(f"<h3>Summary:</h3>", unsafe_allow_html=True)
                            st.write(f"{st.session_state.summary}")
                        
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
