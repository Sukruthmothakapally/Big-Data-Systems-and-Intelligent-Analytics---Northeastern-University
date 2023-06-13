import os
import redis
import streamlit as st
import numpy as np
from datetime import datetime
import openai
import numpy as np
from sentence_transformers import SentenceTransformer

st.title('Part 2')

if "username" in st.session_state:
    st.write(f"Logged in as {st.session_state.username}")

    redis_conn = redis.Redis(host="redis-stack",
                             port=6379,
                             username=os.getenv("DB_USERNAME", ""),
                             password=os.getenv("DB_PASSWORD", ""),
                             decode_responses=False
                             )

    # Get list of companies and dates from Redis
    companies = []
    dates = []
    for key in redis_conn.keys("*:*:*"):
        key_str = key.decode('utf-8')
        company_name, date, part = key_str.split(":")
        companies.append(company_name)
        dates.append(date)
    companies = sorted(list(set(companies)))
    dates = sorted(list(set(dates)))

    # Format dates
    dates = [datetime.strptime(date, '%Y%m%d').strftime('%b %d %Y') for date in dates]

    # User selection
    company = st.selectbox("Select a company", companies)
    date = st.selectbox("Select a date", dates)

    # Get list of parts from Redis
    date_key = datetime.strptime(date, '%b %d %Y').strftime('%Y%m%d')
    parts = []
    for key in redis_conn.keys(f"{company}:{date_key}:*"):
        key_str = key.decode('utf-8')
        company_name, date, part = key_str.split(":")
        parts.append(part)
    parts = sorted(list(set(parts)))

    # User selection
    part = st.selectbox("Select a part of the earnings call", parts)
    embedding_type = st.selectbox("Select an embedding service", ["OpenAI", "SBERT"])

    # Get data from Redis
    key = f"{company}:{date_key}:{part}"
    data = redis_conn.hgetall(key)

    class OpenAI:
        def __init__(self, api_key):
            self.api_key = api_key
            openai.api_key = api_key

        def embed_text(self, text, model="text-embedding-ada-002"):
            text = text.replace("\n", " ")
            return openai.Embedding.create(input=[text], model=model)['data'][0]['embedding']

        def get_top_k_similar_sentences(self, original_sentences, user_input, k=5):
            original_embeddings = [self.embed_text(sentence) for sentence in original_sentences]
            user_input_embedding = self.embed_text(user_input)
            similarities = [np.dot(user_input_embedding, original_embedding) for original_embedding in original_embeddings]
            top_k_indices = np.argsort(similarities)[-k:]
            return [original_sentences[i] for i in top_k_indices]
        
    from sentence_transformers import SentenceTransformer
    sbert_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

    class SBERT:
        def embed_text(self, text):
            text = text.replace("\n", " ")
            return sbert_model.encode([text])

        def get_top_k_similar_sentences(self, original_sentences, user_input, k=5):
            original_embeddings = [self.embed_text(sentence) for sentence in original_sentences]
            user_input_embedding = self.embed_text(user_input)
            similarities = [np.dot(user_input_embedding.reshape(-1), original_embedding.reshape(-1)) for original_embedding in original_embeddings]
            top_k_indices = np.argsort(similarities)[-k:]
            return [original_sentences[i] for i in top_k_indices]

    if data:
        # Decode data
        data = {k.decode('utf-8'): v for k, v in data.items()}

        # Display data
        st.write(f"Earnings call statement: {data['plain_text']}")

        # Display selected embedding
        if embedding_type == "OpenAI":
            api_key = st.text_input("Enter your OpenAI API key")
            openai_embeddings = np.frombuffer(data["openai_embeddings"], dtype=np.float32)
            st.write(f"OpenAI Embeddings: {openai_embeddings}")
            openai_helper = OpenAI(api_key)
            user_input = st.text_input("Enter a sentence to compare with the embeddings")
            if user_input:
                top_5_similar_sentences = openai_helper.get_top_k_similar_sentences(data['plain_text'].decode('utf-8').split('. '), user_input)
                for i, sentence in enumerate(top_5_similar_sentences):
                    st.write(f"{i+1}. {sentence}")
        elif embedding_type == "SBERT":
            sbert_embeddings = np.frombuffer(data["sbert_embeddings"], dtype=np.float32)
            st.write(f"SBERT Embeddings: {sbert_embeddings}")
            sbert_helper = SBERT()
            user_input = st.text_input("Enter a sentence to compare with the embeddings")
            if user_input:
                top_5_similar_sentences = sbert_helper.get_top_k_similar_sentences(data['plain_text'].decode('utf-8').split('. '), user_input)
                for i, sentence in enumerate(top_5_similar_sentences):
                    st.write(f"{i+1}. {sentence}")

    else:
        # Display error message
        st.write(f"Data not found for company: {company} on date: {date} and part: {part}")

else:
    st.write("Please log in first")