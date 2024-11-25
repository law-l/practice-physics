import logging
import time
from datetime import datetime

import gspread
import pandas as pd
import pytz
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials
from streamlit_gsheets import GSheetsConnection

from utils.model import Problem

logger = logging.getLogger(__name__)


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
    is_success = False
    while not is_success:
        try:
            conn = st.connection("gsheets", type=GSheetsConnection)
            df = conn.read(worksheet=worksheet, ttl="10m")
            is_success = True
        except Exception as e:
            logger.info(f"exception: {e}")
            time.sleep(1)

    return df


def _append_row_to_worksheet(worksheet: str, record: list[str]):
    """Append one row to a worksheet in Google Sheet"""
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]

    keyfile_dict = st.secrets.connections.gsheets.to_dict().copy()

    is_success = False
    while not is_success:
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_dict(
                keyfile_dict, scope
            )
            client = gspread.authorize(creds)
            sh = client.open("practice_physics").worksheet(worksheet)
            sh.append_row(record)
            is_success = True
        except:
            time.sleep(1)


def is_valid_user_email(user_email: str) -> bool:
    """Check if a user email has permission to access the app"""
    df = _load_worksheet(worksheet="user_email")
    is_valid = user_email in set(df["user_email"].unique())
    return is_valid


def sample_problem(topic: str) -> dict:
    """Randomly pick a problem based on a topic provided"""
    df = _load_worksheet(worksheet="problem")
    mask = df["topic"] == topic
    problem = Problem.model_validate(
        df.loc[mask, :].sample(n=1).to_dict(orient="records")[0]
    )
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
    if df.shape[0] == 0:
        return df

    # subset activity by selected topic
    mask = df["topic"] == topic
    df = df.loc[mask, :]

    # count number of correct and incorrect attempts
    df["num_correct"] = (df["is_correct"] == 1).astype(int)
    df["num_incorrect"] = (df["is_correct"] == 0).astype(int)

    # compute number of consecutive correct attempts
    df = df.sort_values(by=["user_email", "topic", "timestamp"])
    num_correct_attempts = 5
    cols_to_sum = []
    for num_shift in range(1, num_correct_attempts + 1):
        col = f"is_correct_shift_{num_shift}"
        df[col] = df.groupby(by=["user_email", "topic"])["is_correct"].shift(num_shift)
        cols_to_sum.append(col)
    df["num_consecutive_correct"] = df[cols_to_sum].sum(axis=1)

    # aggregate by user and topic
    df = (
        df.groupby(by=["user_email", "topic"])
        .agg(
            {
                "num_correct": "sum",
                "num_incorrect": "sum",
                "timestamp": "max",
                "num_consecutive_correct": "max",
            }
        )
        .reset_index()
    )
    df["point"] = (
        df["num_correct"] / (df["num_correct"] + df["num_incorrect"]) * 100
    ).astype(int)
    df["rank"] = df["point"].rank(ascending=False).astype(int)
    mask = df["num_consecutive_correct"] >= num_correct_attempts
    df.loc[mask, "status"] = "🟢"
    df.loc[~mask, "status"] = "🔴"

    # generate leaderboard
    df = (
        df.sort_values(by="rank")
        .filter(items=["rank", "user_email", "point", "status", "timestamp"], axis=1)
        .rename(
            columns={
                "rank": "Rank",
                "user_email": "User",
                "point": "Point",
                "timestamp": "Latest attempt",
                "status": "Status",
            }
        )
        .fillna("")
    )

    return df
