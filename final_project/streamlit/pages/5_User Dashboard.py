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

        # Update these paths to the actual paths where the HTML files are served
        data_docs_path_comments = "http://35.235.101.84/comments_suite.html"
        link_text_comments = "Comments table expectations"
        
        data_docs_path_posts = "http://35.235.101.84/posts_suite.html"
        link_text_posts = "Posts table expectations"
        
        # Display the header and the hyperlink for comments expectations
        st.header("Great Expectations Data Analysis -")
        link_markup_comments = f"<a href='{data_docs_path_comments}' target='_blank'>{link_text_comments}</a>"
        
        # Handle opening the HTML file in the browser when the link is clicked
        if st.button(link_text_comments):
            webbrowser.open_new_tab(data_docs_path_comments)
        
        # Display the header and the hyperlink for posts expectations
        link_markup_posts = f"<a href='{data_docs_path_posts}' target='_blank'>{link_text_posts}</a>"
        
        # Handle opening the HTML file in the browser when the link is clicked
        if st.button(link_text_posts):
            webbrowser.open_new_tab(data_docs_path_posts)

    else:
        # Session has timed out, log out user and display login page
        del st.session_state.logged_in
        del st.session_state.last_activity
        
        # Display message asking user to log in
        st.warning("Please Sign In first")
        
else:
    # User is not logged in, display message asking user to log in and display login page
    st.warning("Please Sign In first")
