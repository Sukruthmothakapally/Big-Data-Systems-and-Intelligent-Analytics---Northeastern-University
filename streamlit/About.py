import streamlit as st

st.set_page_config(page_title="Stack AI", page_icon="👋")

st.markdown("""
<style>
    .center {
        display: block;
        margin-left: auto;
        margin-right: auto;
        text-align: center;
    }
    .green {
        color: green;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='center'>Welcome to StackAI</h1>", unsafe_allow_html=True)

st.markdown("<h2 class='green'>Features</h2>", unsafe_allow_html=True)
st.markdown("<h3>Ask a question and STackAI will find the most similar topics using StackOverflow database</h3>", unsafe_allow_html=True)
