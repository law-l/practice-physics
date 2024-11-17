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
    df = conn.read(worksheet=worksheet, ttl="10m")
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
    df = df.drop(columns="topic")
    problem = Problem.model_validate(df.loc[mask, :].sample(n=1).to_dict(orient="records")[0])
    return problem


def log_submission(user: str, problem_id: int, correct: bool):
    """Log submission into activity worksheet"""

    record = [user, problem_id, correct, _get_eastern_timestamp()]
    _append_row_to_worksheet(worksheet="activity", record=record)


def get_topics() -> list[str]:
    """Get a list of available topics from problems"""
    df = _load_worksheet(worksheet="problem")
    topics = list(df["topic"].unique())
    return topics