import os
import redis
import streamlit as st
import numpy as np
from datetime import datetime

st.title('Company Data')

redis_conn = redis.Redis(host="redis-stack",
                         port=6379,
                         username=os.getenv("DB_USERNAME", ""),
                         password=os.getenv("DB_PASSWORD", ""),
                         decode_responses=False
                         )

# Get list of companies and dates from Redis
companies = []
dates = []
for key in redis_conn.keys("*:*:1"):
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

# Get data from Redis
date_key = datetime.strptime(date, '%b %d %Y').strftime('%Y%m%d')
key = f"{company}:{date_key}:1"
data = redis_conn.hgetall(key)

if data:
    # Decode data
    data = {k.decode('utf-8'): v for k, v in data.items()}

    # Display data
    st.write(f"Ticker: {data['ticker']}")
    st.write(f"Company Name: {data['company_name']}")
    st.write(f"Date: {data['date']}")
    st.write(f"Part: {data['Part']}")
    st.write(f"Plain Text: {data['plain_text']}")

    # Display embeddings
    #to convert string to numpy array as redis stores data as string and we need to convert it back to numpy array
    sbert_embeddings = np.frombuffer(data["sbert_embeddings"], dtype=np.float32)
    openai_embeddings = np.frombuffer(data["openai_embeddings"], dtype=np.float32)
    st.write(f"SBERT Embeddings: {sbert_embeddings}")
    st.write(f"OpenAI Embeddings: {openai_embeddings}")

else:
    #Display error message
    st.write(f"Data not found for company: {company} on date: {date}")