import streamlit as st

from utils.db import get_topics, is_valid_user_email, log_submission, sample_problem

st.set_page_config(page_title="Practice", page_icon="🧠")

# initialize session_state
if "is_reloaded" not in st.session_state or st.session_state["is_reloaded"]:
    st.session_state["topic"] = None
    st.session_state["problem"] = None
    st.session_state["is_submitted"] = False
    st.session_state["response"] = None
    st.session_state["is_reloaded"] = False

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

    # pick a topic
    topic = st.selectbox("Topic", get_topics())
    if topic != st.session_state["topic"]:
        st.session_state["topic"] = topic
        st.session_state["problem"] = sample_problem(topic)
        st.session_state["is_submitted"] = False

    problem = st.session_state["problem"]

    # display question
    st.subheader("Problem")
    st.write(f"[ID: {problem.id}] {problem.question}")

    # display options
    response = st.radio(
        label="Select your answer and click submit",
        options=[
            problem.option_1,
            problem.option_2,
            problem.option_3,
            problem.option_4,
        ],
        disabled=st.session_state["is_submitted"],
    )

    # if the submit button has not been clicked, keep track of user repsonse.
    # once submit button has been clicked, stop updating user response.
    if not st.session_state["is_submitted"]:
        st.session_state["response"] = response

    col1, col2, col3 = st.columns(3)

    # display submit button
    with col1:
        is_submitted = st.button(
            label="Submit",
            disabled=st.session_state["is_submitted"],
        )

    # if the submit button has been clicked the first time, log submission
    if is_submitted and not st.session_state["is_submitted"]:
        log_submission(
            problem=problem,
            user=st.session_state["user_email"],
            correct=st.session_state["response"] == problem.answer,
        )

    # if the submit button has ever been clicked, then problem is considered submitted.
    if is_submitted or st.session_state["is_submitted"]:
        st.session_state["is_submitted"] = True

    # if the submit button has ever been clicked, check answers
    if st.session_state["is_submitted"]:
        if st.session_state["response"] == problem.answer:
            st.success(f"The answer is correct.")
        else:
            st.error(f"The answer is incorrect.")

    # if the submit button has ever been clicked, display show solution button
    if st.session_state["is_submitted"]:
        with col2:
            is_solution_shown = st.toggle(label="Show solution", key="show_solution")
        if is_solution_shown:
            st.subheader("Solution")
            st.write(problem.explanation)

    with col3:
        # reload button
        if st.button("Reload"):
            st.session_state["is_submitted"] = False
            st.session_state["is_reloaded"] = True
            st.rerun()
