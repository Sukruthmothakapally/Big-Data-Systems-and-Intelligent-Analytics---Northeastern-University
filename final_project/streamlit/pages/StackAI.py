from google.cloud import bigquery
import pandas as pd
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
# from langchain.llms.openai import OpenAI
# from langchain.chains.summarize import load_summarize_chain
# from scipy.spatial.distance import cdist
# import openai
import streamlit as st

st.markdown("# Topic relevance search")
st.markdown("## Ask a question and we'll find the most relevant topics for you using stackoverflow database.")

# Set up BigQuery client with explicit project ID
bq_client = bigquery.Client(project='stackai-394819')

# Set up query for posts
query1 = """
    SELECT *
    FROM `stackai-394819.StackAI.posts_cleaned`
"""

# Run query and fetch results into pandas DataFrame
df = bq_client.query(query1).to_dataframe()

# Set up query for comments
query2 = """
    SELECT *
    FROM `stackai-394819.StackAI.comments_cleaned`
"""

# Run query and fetch results into pandas DataFrame
df2 = bq_client.query(query2).to_dataframe()

# Load the pre-trained Sentence Transformers model
model = SentenceTransformer('distilbert-base-nli-stsb-mean-tokens')

# Preprocessing function to convert tags from string to list
def process_tags(Tags):
    if pd.isna(Tags):  # Handle NaN values
        return []      # Return an empty list for NaN values
    return Tags.split(',')

# Apply the preprocessing to the 'Tags' column (uppercase "T")
df['question_tags'] = df['question_tags'].apply(process_tags)

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
        print(f"No relevant data found for the tag '{user_input_tag}'.")
        return []

    # Fetch embeddings from BigQuery table
    data_embeddings = np.array(filtered_data['embeddings'].tolist())

    # Generate embedding for user input
    user_embedding = generate_embeddings([user_input])

    # Calculate cosine similarity between user input and data embeddings
    similarity_scores = cosine_similarity(user_embedding, data_embeddings)[0]

    # Sort the data by similarity scores in descending order and select top 5 rows
    top_indices = np.argsort(similarity_scores)[::-1][:5]
    
    top_similar_topics = filtered_data.iloc[top_indices][['question_id', 'question_title', 'question_body', 'accepted_answer']].to_dict('records')
    
    top_similarity_scores = similarity_scores[top_indices]

    return top_similar_topics, top_similarity_scores

    if __name__ == "__main__":
    # user can ask a question
    st.write("Enter your question : ")
    user_question = st.text_input("")
    # Get unique tags from the 'question_tags' column of the 'df' DataFrame
    unique_tags = pd.Series(df['question_tags'].sum()).unique()

    # User can select any tag from the list of unique tags
    user_tag = st.selectbox("Select a category:", unique_tags)
    

    similar_topics, similarity_scores = topic_relevance_search(user_question, user_tag)
    
    st.write("Most similar topics:")
    
    for i in range(len(similar_topics)):
        question_id, question_title, question_body, accepted_answer = similar_topics[i]['question_id'], similar_topics[i]['question_title'], similar_topics[i]['question_body'], similar_topics[i]['accepted_answer']
        
        st.write(f"{i+1}. Question ID: {question_id} : {question_title} (similarity score: {similarity_scores[i]:.2f})")
