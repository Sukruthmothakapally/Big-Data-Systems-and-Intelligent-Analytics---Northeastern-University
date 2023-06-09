import os
import json
import requests
import streamlit as st

BASE_URL = os.getenv("API_URL", "http://localhost:8003")

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.title("Demo - FastAPI + Streamlit")

st.divider()

with st.form("sentence_embeddings", clear_on_submit=False):
    st.subheader("Sentence Embeddings")

    user_input_sentences = st.text_area(
        "Enter a sentences", value="", placeholder="Enter sentences", key="user-input")
    api_key = st.text_input(label="API Key", value="", type="password",
                            placeholder="Enter you API Key", key="api-key")
    service_selection = st.selectbox(
        'Which service would you like to use?', ('HuggingFace', 'OpenAI', 'Cohere'))

    submitted = st.form_submit_button("Submit")
    if submitted:
        if st.spinner("Loading..."):
            url = f"{BASE_URL}/api/v1/tokenize"
            payload = {
                "service": service_selection.lower(),
                "apikey": api_key,
                "content": [val.strip() for val in user_input_sentences.split('|')]
            }
            json_payload = json.dumps(payload)
            headers = {'Content-Type': 'application/json'}
            response = requests.request(
                "POST", url, headers=headers, data=json_payload)
            st.json(response.text)


st.divider()

# Run the app
# streamlit run main.py