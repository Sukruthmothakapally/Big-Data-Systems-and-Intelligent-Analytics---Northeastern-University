import streamlit as st

st.set_page_config(page_title="DAMG 7245", page_icon="👋")

st.sidebar.success("Assignment 3 sections")
st.title("Assignment 3")

st.markdown("""### Azure Computer Vision -  is a cloud-based service that provides developers with access to advanced algorithms for processing images and returning information. It can analyze visual content in different ways based on inputs and user choices.""")
st.write("One of the features of Azure Computer Vision is image analysis, which can extract rich information from images, such as the objects and actions depicted in the image, the colors and styles used, and even the emotions expressed by any people in the image.")
#enter api keys in the sidebar
st.sidebar.markdown("""### Enter Azure credentials""")
#sidebar api key user input
key = st.sidebar.text_input("Your Azure key", type="password")
endpoint = st.sidebar.text_input("Your Azure endpoint", type="password")

if st.sidebar.button("Save"):
    st.session_state.key = key
    st.session_state.endpoint = endpoint
