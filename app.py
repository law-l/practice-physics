from util.model import Problem

import streamlit as st
import os
import pandas as pd


@st.cache_data()
def load_problems(sheet_url: str) -> pd.DataFrame:
    """Load all problems from Google Sheet"""
    csv_export_url = sheet_url.replace('/edit?gid=', '/export?format=csv&gid=')
    df = pd.read_csv(csv_export_url).astype(str)
    return df


def sample_problem(df: pd.DataFrame) -> dict:
    """Randomly pick a problem"""
    return df.sample(1).to_dict(orient="records")[0]


df_problems = load_problems(st.secrets["GSHEET_PROBLEMS"])

# initialize session_state
if "is_reloaded" not in st.session_state or st.session_state["is_reloaded"]:

    # initialize variables
    st.session_state["is_submitted"] = False
    st.session_state["is_solution_shown"] = False
    st.session_state["response"] = None
    st.session_state["is_reloaded"] = False
    st.session_state["problem"] = sample_problem(df_problems)

    # # get data
    # sheet_url = os.environ["GSHEET_PROBLEM"]
    # csv_export_url = sheet_url.replace('/edit?gid=', '/export?format=csv&gid=')
    # st.session_state["problem"] = pd.read_csv(csv_export_url).astype(str).sample(1).to_dict(orient="records")[0]

# reload button
if st.button("Reload"):
    st.session_state["is_submitted"] = False
    st.session_state["is_reloaded"] = True
    st.rerun()

problem = Problem.model_validate(st.session_state["problem"])
st.subheader("Question")
st.write(f"[ID: {problem.id}] {problem.question}")

response = st.radio(
    label="Select your answer and click submit", 
    options=[problem.option_1, problem.option_2, problem.option_3, problem.option_4],
    disabled=st.session_state["is_submitted"],
)
if not st.session_state["is_submitted"]:
    st.session_state["response"] = response

is_submitted = st.button(
    label="Submit",
    disabled=st.session_state["is_submitted"],
)
if is_submitted or st.session_state["is_submitted"]:
    st.session_state["is_submitted"] = True

if st.session_state["is_submitted"]:
    if st.session_state["response"] == problem.answer:
        st.success(f"That is correct.")
    else:
        st.error(f"That is incorrect.")

if st.session_state["is_submitted"]:
    is_solution_shown = st.button(label="Show solution")
    if is_solution_shown or st.session_state["is_solution_shown"]:
        st.session_state["is_solution_shown"] = True
        st.subheader("Solution")
        st.markdown(problem.explanation)