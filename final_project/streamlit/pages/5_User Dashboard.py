import streamlit as st

from datetime import timedelta
from datetime import datetime
import pandas as pd
import webbrowser

# Check if user is logged in and session is still valid
if "logged_in" in st.session_state and "last_activity" in st.session_state:
    time_since_last_activity = datetime.now() - st.session_state.last_activity
    if time_since_last_activity < timedelta(minutes=15):
        # Session is still valid, update last activity time
        st.session_state.last_activity = datetime.now()

        # Display logout button
        if st.sidebar.button("Logout"):
            del st.session_state.logged_in
            del st.session_state.last_activity
            #rerun the page
            st.experimental_rerun()
        
        # Display welcome message with user's first name and last name
        st.title(f"{st.session_state.first_name} {st.session_state.last_name}'s Dashboard")

        # search history
        st.header("Search History - ")

        # Retrieve the stored search history from session state
        search_history = getattr(st.session_state, "search_history", [])

        if not search_history:
            st.markdown("<h4>No history available</h4>", unsafe_allow_html=True)
        else:
            # Create a data frame from the search history
            df = pd.DataFrame(search_history)

            # Rename the columns
            df.columns = ["Question", "Most Similar Topic"]

            # Function to render the "Most Similar Topic" column as clickable links
            def render_link(row):
                return f'<a href="{row}" target="_blank">{row}</a>'

            # Apply the function to the "Most Similar Topic" column
            df["Most Similar Topic"] = df["Most Similar Topic"].apply(render_link)

            # Display the modified table with clickable links
            st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)

            # Add a hyperlink to the Great Expectations Data Docs index.html file
        data_docs_path = r"C:\\Users\\Dell\\OneDrive - Northeastern University\\courses\\big data and intl analytics\\DAMG7245-Summer2023\\final_project\\great_expectations\\uncommitted\\data_docs\\local_site\\expectations\\comments_suite.html"
        link_text = "Comments table expectations"

        data_docs_path2 = r"C:\\Users\\Dell\\OneDrive - Northeastern University\\courses\\big data and intl analytics\\DAMG7245-Summer2023\\final_project\\great_expectations\\uncommitted\\data_docs\\local_site\\expectations\\posts_suite.html"
        link_text2 = "Posts table expectations"
        
        # Display the header and the hyperlink
        st.header("Great Expectations Data Analysis -")
        link_markup2 = f"<a href='{data_docs_path2}' target='_blank'>{link_text2}</a>"

        # Handle opening the index.html file in the browser when the link is clicked
        if st.button(link_text2):
            webbrowser.open_new_tab(data_docs_path2)
        
        # Display the header and the hyperlink
        link_markup = f"<a href='{data_docs_path}' target='_blank'>{link_text}</a>"

        # Handle opening the index.html file in the browser when the link is clicked
        if st.button(link_text):
            webbrowser.open_new_tab(data_docs_path)

    else:
        # Session has timed out, log out user and display login page
        del st.session_state.logged_in
        del st.session_state.last_activity
        
        # Display message asking user to log in
        st.warning("Please Sign In first")
        
else:
    # User is not logged in, display message asking user to log in and display login page
    st.warning("Please Sign In first")
