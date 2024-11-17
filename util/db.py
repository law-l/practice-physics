from datetime import datetime

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


def sample_problem() -> dict:
    """Randomly pick a problem"""
    df = _load_worksheet(worksheet="problem")
    problem = df.sample(n=1).to_dict(orient="records")[0]
    return problem


def log_submission(user: str, problem_id: int, correct: bool):
    """Log submission into activity worksheet"""

    record = [user, problem_id, correct, _get_eastern_timestamp()]
    _append_row_to_worksheet(worksheet="activity", record=record)
