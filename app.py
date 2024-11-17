import streamlit as st

from util.db import log_submission, sample_problem
from util.model import Problem

# initialize session_state
if "is_reloaded" not in st.session_state or st.session_state["is_reloaded"]:

    # initialize variables
    st.session_state["is_submitted"] = False
    st.session_state["is_solution_shown"] = False
    st.session_state["response"] = None
    st.session_state["is_reloaded"] = False
    st.session_state["problem"] = sample_problem()

# make sure problem is in the correct format
problem = Problem.model_validate(st.session_state["problem"])

# display question
st.subheader("Question")
st.write(f"[ID: {problem.id}] {problem.question}")

# display options
response = st.radio(
    label="Select your answer and click submit",
    options=[problem.option_1, problem.option_2, problem.option_3, problem.option_4],
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
with col3:
    # reload button
    if st.button("Reload"):
        st.session_state["is_submitted"] = False
        st.session_state["is_reloaded"] = True
        st.rerun()

# if the submit button has been clicked the first time, log submission
if is_submitted and not st.session_state["is_submitted"]:
    log_submission(
        user="test_user",
        problem_id=problem.id,
        correct=st.session_state["response"] == problem.answer,
    )

# if the submit button has ever been clicked, then problem is considered submitted.
if is_submitted or st.session_state["is_submitted"]:
    st.session_state["is_submitted"] = True

# if the submit button has ever been clicked, check answers
if st.session_state["is_submitted"]:
    if st.session_state["response"] == problem.answer:
        st.success(f"That is correct.")
    else:
        st.error(f"That is incorrect.")

# if the submit button has ever been clicked, display show solution button
if st.session_state["is_submitted"]:
    with col2:
        is_solution_shown = st.button(label="Show solution")
    if is_solution_shown or st.session_state["is_solution_shown"]:
        st.session_state["is_solution_shown"] = True
        st.subheader("Solution")
        st.markdown(problem.explanation)
