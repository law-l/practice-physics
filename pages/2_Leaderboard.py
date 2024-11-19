from util.db import get_topics, get_leaderboard

import streamlit as st

st.set_page_config(page_title="Leaderboard", page_icon="🏆")

topic = st.selectbox("Topic", get_topics())
st.subheader(f"Leaderboard for topic: {topic}")
st.caption("(sorted by the percentage of correct attempts in a descending order)")
st.dataframe(get_leaderboard(topic), hide_index=True)