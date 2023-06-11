import os
import redis
import streamlit as st

st.title('Company Data')

redis_conn = redis.Redis(host="localhost",
                         port=30001,
                         username=os.getenv("DB_USERNAME", ""),
                         password=os.getenv("DB_PASSWORD", ""),
                         decode_responses=True
                         )

# Get list of companies and dates from Redis
companies = []
dates = []
for key in redis_conn.keys("*:*"):
    ticker, date = key.split(":")
    companies.append(ticker)
    dates.append(date)
companies = sorted(list(set(companies)))
dates = sorted(list(set(dates)))

# User selection
company = st.selectbox("Select a company", companies)
date = st.selectbox("Select a date", dates)

# Get data from Redis
key = f"{company}:{date}"
data = redis_conn.hgetall(key)

if data:
    # Display data
    st.write(f"Ticker: {data['ticker']}")
    st.write(f"Company Name: {data['company_name']}")
    st.write(f"Date: {data['date']}")
    st.write(f"Plain Text: {data['plain_text']}")

else:
    #Display error message
    st.write(f"Data not found for company: {company} on date: {date}") 
