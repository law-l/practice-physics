import streamlit as st

from utils.db import get_leaderboard, get_topics, is_valid_user_email

st.set_page_config(page_title="Leaderboard", page_icon="🏆")

# if user has not signed in, ask them to sign in.
if "user_email" not in st.session_state:
    user_email = st.text_input("Email address")
    is_signed_in = st.button("Sign in")
    if is_signed_in:
        is_valid = is_valid_user_email(user_email)
        if user_email and is_valid:
            st.session_state["user_email"] = user_email
            st.rerun()
        else:
            st.error(f"{user_email} does not have permission to access this app.")
else:
    st.info(f"You are currently signed in as {st.session_state['user_email']}.")
    topic = st.selectbox("Topic", get_topics())
    st.subheader(f"Leaderboard for topic: {topic}")
    st.dataframe(get_leaderboard(topic), hide_index=True)
