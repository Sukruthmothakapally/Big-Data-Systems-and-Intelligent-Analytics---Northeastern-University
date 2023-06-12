import os
import redis
import streamlit as st
import numpy as np
from datetime import datetime

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

    if data:
        # Decode data
        data = {k.decode('utf-8'): v for k, v in data.items()}

        # Display data
        st.write(f"Earnings call statement: {data['plain_text']}")

        # Display selected embedding
        if embedding_type == "OpenAI":
            openai_embeddings = np.frombuffer(data["openai_embeddings"], dtype=np.float32)
            st.write(f"OpenAI Embeddings: {openai_embeddings}")
        elif embedding_type == "SBERT":
            sbert_embeddings = np.frombuffer(data["sbert_embeddings"], dtype=np.float32)
            st.write(f"SBERT Embeddings: {sbert_embeddings}")
        #textbox to enter a sentence
        st.text_input("Enter a sentence to compare with the embeddings")

    else:
        # Display error message
        st.write(f"Data not found for company: {company} on date: {date} and part: {part}")

else:
    st.write("Please log in first")
