from util.db import get_topics, get_leaderboard

import streamlit as st

st.set_page_config(page_title="Leaderboard", page_icon="🏆")

topic = st.selectbox("Topic", get_topics())
st.subheader(f"Leaderboard for topic: {topic}")
st.caption("(sorted by the percentage of correct attempts in a descending order)")
st.bar_chart(
    get_leaderboard(topic),
    x="user_email",
    x_label="",
    y=["num_correct", "num_incorrect"],
    y_label="",
    color=["#a5d46a", "#ffa080"],
    horizontal=True,
    use_container_width=True,
)