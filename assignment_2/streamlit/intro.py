import streamlit as st

# page = st.experimental_get_query_params().get("page", ["userlogin"])[0]
# #below is the code to add the pages to the sidebar and the page title to the browser tab
# if page == "user_login":
#     import pages.userlogin
# elif page == "part_2":
#     import pages.part2

st.set_page_config(page_title="DAMG 7245", page_icon="👋")

st.sidebar.success("Assignment 2 sections")
st.title("Assignment 2")

st.markdown("""### Case Details 
            Intelligence Co has hired you as a software engineer. You are a fintech that intends
            to use data and analytics to help analysts make investment recommendations. They
            track many stocks and intend to build an on-the-fly document summarization engine
            for earnings call transcripts.

            The specification of the project is as follows:
            
            Intelligence Co reviewed the solution using Redis (Assignment 1) and now thinks they
            need to evaluate other products too. They intend to try Cloud SQL with Postgres SQL
            and Pine cone for the following use case. The company expects transcripts to be in the
            format and the naming convention""")
