from datetime import datetime
from util.model import Problem

import gspread
import pandas as pd
import pytz
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials
from streamlit_gsheets import GSheetsConnection


def _get_eastern_timestamp() -> str:
    """Get eastern time zone timestamp"""
    # Get the current time in UTC
    now_utc = datetime.now(pytz.utc)

    # Convert to Eastern Time
    eastern_timezone = pytz.timezone("America/New_York")
    now_eastern = now_utc.astimezone(eastern_timezone)

    # Format the timestamp
    timestamp = now_eastern.strftime("%Y-%m-%d %H:%M:%S %Z%z")

    return timestamp


def _load_worksheet(worksheet: str) -> pd.DataFrame:
    """Load worksheet from Google Sheet"""
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(worksheet=worksheet)
    return df


def _append_row_to_worksheet(worksheet: str, record: list[str]):
    """Append one row to a worksheet in Google Sheet"""
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]

    keyfile_dict = st.secrets.connections.gsheets.to_dict().copy()

    creds = ServiceAccountCredentials.from_json_keyfile_dict(keyfile_dict, scope)
    client = gspread.authorize(creds)

    sh = client.open("practice_physics").worksheet(worksheet)
    sh.append_row(record)


def is_valid_user_email(user_email: str) -> bool:
    """Check if a user email has permission to access the app"""
    df = _load_worksheet(worksheet="user_email")
    is_valid = user_email in set(df["user_email"].unique())
    return is_valid


def sample_problem(topic: str) -> dict:
    """Randomly pick a problem based on a topic provided"""
    df = _load_worksheet(worksheet="problem")
    mask = df["topic"] == topic
    problem = Problem.model_validate(df.loc[mask, :].sample(n=1).to_dict(orient="records")[0])
    return problem


def log_submission(problem: Problem, user: str, correct: bool):
    """Log submission into activity worksheet"""
    record = [user, problem.topic, problem.id, correct, _get_eastern_timestamp()]
    _append_row_to_worksheet(worksheet="activity", record=record)


def get_topics() -> list[str]:
    """Get a list of available topics from problems"""
    df = _load_worksheet(worksheet="problem")
    topics = list(df["topic"].unique())
    return topics


def get_leaderboard(topic: str) -> pd.DataFrame:
    """Get a DataFrame for leaderboard"""
    df = _load_worksheet(worksheet="activity")

    # subset activity by selected topic
    mask = df["topic"] == topic
    df = df.loc[mask, :]

    # count number of correct and incorrect attempts
    df["num_correct"] = (df["is_correct"] == 1).astype(int)
    df["num_incorrect"] = (df["is_correct"] == 0).astype(int)

    # compute percentage of correct attempts
    df = df.groupby(by=["user_email", "topic"])[["num_correct", "num_incorrect"]].sum().reset_index()
    df["pct_correct"] = df["num_correct"]/(df["num_correct"]+df["num_incorrect"])

    # compute ranking
    df["rank"] = df["pct_correct"].rank(ascending = False).astype(int)
    df = df.sort_values(by = "rank")

    # # output final df
    # keep_cols = ["#", "user_email", "pct_correct"]
    # df = df.loc[:, keep_cols]
    # df.style.bar(subset = ["pct_correct"], color = 'skyblue')

    return df

# def get_leaderboard(topic: str) -> pd.DataFrame:
#     """Get a DataFrame for leaderboard"""
#     df = _load_worksheet(worksheet="activity")

#     # subset activity by selected topic
#     mask = df["topic"] == topic
#     df = df.loc[mask, :]

#     df["count"] = 1
#     df["result"] = df["is_correct"].map({1: "correct", 0: "incorrect"})

#     # compute percentage of correct attempts
#     df = df.groupby(by=["user_email", "result"])["timestamp"].nunique().reset_index().rename({"timestamp": "count"}, axis = 1)
#     df["pct"] = df["count"]/df.groupby(by=["user_email"])["count"].transform("sum")
#     mask = df["result"] == "correct"
#     df.loc[mask, "pct_correct"] = df.loc[mask, "pct"]
#     df = df.sort_values(by = "pct_correct", ascending = False)

#     return df
