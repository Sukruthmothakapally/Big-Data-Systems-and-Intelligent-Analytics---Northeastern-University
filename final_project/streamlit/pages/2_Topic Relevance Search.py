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

        st.markdown("<h1 class='center'>Topic Relevance Search </h1>", unsafe_allow_html=True)

        with st.spinner("Page loading..."):
            from google.cloud import bigquery
            import pandas as pd
            from sentence_transformers import SentenceTransformer
            import numpy as np
            from sklearn.metrics.pairwise import cosine_similarity
            from langchain.llms.openai import OpenAI
            from langchain.chains.summarize import load_summarize_chain
            #from scipy.spatial.distance import cdist
            import openai


            @st.cache_data(show_spinner=False)
            def load_data():
                # Set up BigQuery client with explicit project ID
                bq_client = bigquery.Client(project='stackai-394819')

                # Set up query for posts
                query1 = """
                    SELECT *
                    FROM `stackai-394819.StackAI.posts_cleaned`
                """

                query2 = """
                    SELECT *
                    FROM `stackai-394819.StackAI.comments_cleaned`
                """

                # Run query and fetch results into pandas DataFrame
                df = bq_client.query(query1).to_dataframe()
                df2 = bq_client.query(query2).to_dataframe()
                
                return df, df2

            df, df2 = load_data()

            # Store the df2 DataFrame in session state
            st.session_state.df2 = df2

            # Preprocessing function to convert tags from string to list
            @st.cache_data(show_spinner=False)
            def process_tags(Tags):
                if pd.isna(Tags):  # Handle NaN values
                    return []      # Return an empty list for NaN values
                return Tags.split(',')

            @st.cache_data(show_spinner=False)
            def generate_embeddings(text):
                # Load the pre-trained Sentence Transformers model
                model = SentenceTransformer('distilbert-base-nli-stsb-mean-tokens')
                embeddings = model.encode(text)
                return embeddings

            @st.cache_data(show_spinner=False)
            def preprocess_data(df):
                # Apply the preprocessing to the 'Tags' column (uppercase "T")
                df['question_tags'] = df['question_tags'].apply(process_tags)
                
                # Get unique tags from the 'question_tags' column of the 'df' DataFrame
                unique_tags = pd.Series(df['question_tags'].sum()).unique()
                
                return df, unique_tags

            df, unique_tags = preprocess_data(df)

            # User can select any tag from the list of unique tags
            st.markdown("<h3 class='center'>Select a category</h3>", unsafe_allow_html=True)
            user_tag = st.selectbox("",unique_tags)

            # user can ask a question
            st.markdown("<h3 class='center'>Enter your question</h3>", unsafe_allow_html=True)
            user_question = st.text_input("")

            # Store the value of the user_question variable in session state
            st.session_state.user_question = user_question

            # Check if the user entered a question
            if user_question:
                # Store the question in the session state
                if "questions" not in st.session_state:
                    st.session_state.questions = []
                st.session_state.questions.append(user_question)


            def filter_data(user_input_tag):
                filtered_data = df

                # Keep only data for the user input tag
                filtered_data = filtered_data[filtered_data['question_tags'].apply(lambda tags: user_input_tag in tags)]

                return filtered_data

            def topic_relevance_search(user_input, user_input_tag):
                # Filter data based on user input tag and "PostTypeId"
                filtered_data = filter_data(user_input_tag)

                # Check if there is relevant data for the user input tag
                if filtered_data.empty:
                    st.write(f"No relevant data found for the tag '{user_input_tag}'.")
                    return []

                # Fetch embeddings from BigQuery table
                data_embeddings = np.array(filtered_data['embeddings'].tolist())

                # Generate embedding for user input
                user_embedding = generate_embeddings([user_input])

                # Calculate cosine similarity between user input and data embeddings
                similarity_scores = cosine_similarity(user_embedding, data_embeddings)[0]

                # Sort the data by similarity scores in descending order and select top 5 rows
                top_indices = np.argsort(similarity_scores)[::-1][:5]
                
                top_similar_topics = filtered_data.iloc[top_indices][['question_id', 'question_title', 'question_body', 'accepted_answer','question_creation_date','question_score','question_view_count','answer_count','comment_count', 'accepted_answer_creation_date','accepted_answer_view_count', 'accepted_answer_score', 'owner_reputation', 'owner_badge']].to_dict('records')
                
                top_similarity_scores = similarity_scores[top_indices]

                return top_similar_topics, top_similarity_scores

            with st.spinner("Loading..."):
                # Add a "Generate result" button
                if st.button("Generate result"):
                    # Check if user input is not empty
                    if user_question and user_tag:
                        similar_topics, similarity_scores = topic_relevance_search(user_question, user_tag)

                        # Store the result in session state
                        st.session_state.similar_topics = similar_topics
                        st.session_state.similarity_scores = similarity_scores

                        #result 1
                        st.write("<h3>Most similar topics:</h3", unsafe_allow_html=True)
                        for i in range(len(similar_topics)):
                            question_id, question_title, question_body, accepted_answer, accepted_answer_creation_date, accepted_answer_view_count, accepted_answer_score, owner_reputation, owner_badge = similar_topics[i]['question_id'], similar_topics[i]['question_title'], similar_topics[i]['question_body'], similar_topics[i]['accepted_answer'], similar_topics[i]['accepted_answer_creation_date'], similar_topics[i]['accepted_answer_view_count'], similar_topics[i]['accepted_answer_score'], similar_topics[i]['owner_reputation'], similar_topics[i]['owner_badge']
                            # Color-code the similarity score based on its value
                            if similarity_scores[i] >= 0.75:
                                color = "green"
                            elif similarity_scores[i] >= 0.5:
                                color = "orange"
                            else:
                                color = "red"
                            # Convert the similarity score to a percentage
                            similarity_percentage = similarity_scores[i] * 100

                            # Add a hyperlink to the Stack Overflow page for each topic
                            result_topics=f"<h4>{i+1}. <a href='https://stackoverflow.com/questions/{question_id}/{question_title}' target='_blank'>{question_title}</a> (similarity score: <span style='color: {color};'>{similarity_percentage:.0f}%</span>)</h4>"
                            
                            
                            # Add a hyperlink to the Stack Overflow page for each topic
                            st.markdown(result_topics, unsafe_allow_html=True)

                            # Store the most similar topic in the session state
                            if i == 0:

                                # Initialize an empty list to store the search history
                                if "search_history" not in st.session_state:
                                    st.session_state.search_history = []

                                # Store the user's question and first result in session state
                                st.session_state.search_history.append({"question": user_question, "first_result": result_topics})

                            # Get the details of the selected topic
                            selected_topic = similar_topics[i]
                            question_creation_date = selected_topic['question_creation_date']
                            question_score = selected_topic['question_score']
                            question_view_count = selected_topic['question_view_count']
                            answer_count = selected_topic['answer_count']
                            comment_count = selected_topic['comment_count']

                            # Set the color of the question view count based on its value
                            if question_view_count > 1000:
                                view_count_color = "green"
                            elif question_view_count >= 500:
                                view_count_color = "orange"
                            else:
                                view_count_color = "red"

                            # Set the color of the question score based on its value
                            if question_score > 5:
                                score_color = "green"
                            elif question_score >= 1:
                                score_color = "orange"
                            else:
                                score_color = "red"

                            # Set the color of the answer count based on its value
                            if answer_count > 5:
                                answer_count_color = "green"
                            elif answer_count >= 1:
                                answer_count_color = "orange"
                            else:
                                answer_count_color = "red"

                            # Set the color of the comment count based on its value
                            if comment_count > 5:
                                comment_count_color = "green"
                            elif comment_count >= 1:
                                comment_count_color = "orange"
                            else:
                                comment_count_color = "red"

                            # Create an HTML table to display the details of the selected topic
                            table_html = f"""
                                <table>
                                    <tr>
                                        <th>Question creation date</th>
                                        <td>{question_creation_date}</td>
                                    </tr>
                                    <tr>
                                        <th>Question view count</th>
                                        <td style="color: {view_count_color};">{question_view_count}</td>
                                    </tr>
                                    <tr>
                                        <th>Question score</th>
                                        <td style="color: {score_color};">{question_score}</td>
                                    </tr>
                                    <tr>
                                        <th>Answer count</th>
                                        <td style="color: {answer_count_color};">{answer_count}</td>
                                    </tr>
                                    <tr>
                                        <th>Comment count</th>
                                        <td style="color: {comment_count_color};">{comment_count}</td>
                                    </tr>
                                </table>
                            """
                            st.write(table_html, unsafe_allow_html=True)


                    else:
                        st.write("Please enter a question and select a category before generating the result.")
    else:
            # Session has timed out, log out user and display login page
            del st.session_state.logged_in
            del st.session_state.last_activity
            
            # Display message asking user to log in
            st.warning("Please Sign In first")
            
else:
    # User is not logged in, display message asking user to log in and display login page
    st.warning("Please Sign In first")                






