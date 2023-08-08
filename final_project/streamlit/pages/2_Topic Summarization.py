import streamlit as st

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
        selected_radio = st.radio("Choose an option:", radio_options)

        # Add a submit button to process the selected option with loading spinner
        with st.spinner("Loading..."):
            if st.form_submit_button("Submit"): 

                if selected_radio == "View details":
                    # Get the index of the selected topic
                    selected_index = options.index(selected_option)
                    
                    # Get the details of the selected topic
                    selected_topic = similar_topics[selected_index]
                    question_id, question_title, question_body, accepted_answer = selected_topic['question_id'], selected_topic['question_title'], selected_topic['question_body'], selected_topic['accepted_answer']
                    
                    if pd.isna(accepted_answer):
                        st.markdown("<h4 style='color:red'>No accepted answer</h4>", unsafe_allow_html=True)
                    else:
                        # Render the HTML content of the accepted answer
                        st.markdown(f"<h4 style='color:green'>Accepted answer:</h4> {accepted_answer}", unsafe_allow_html=True)

                    post_comments = df2[df2['post_id'] == question_id]

                    st.markdown(f"<h4>Question body:{question_body}</h4>", unsafe_allow_html=True)

                    comments_text = ""
                    if not post_comments.empty:
                        st.markdown("<h4>Comments:</h4>", unsafe_allow_html=True)
                        for comment in post_comments['text']:
                            st.write(f"\t- {comment}")
                            comments_text += f"\n- {comment}"
                    
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
