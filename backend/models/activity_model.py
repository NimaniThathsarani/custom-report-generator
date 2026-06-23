"""
backend/models/activity_model.py
=================================
Data-access layer for the User Activity Report.

Public API
----------
get_activity_data(filters: dict) -> pd.DataFrame
get_activity_summary(filters: dict) -> dict

filters keys (all optional)
----------------------------
    start_date    : str   "YYYY-MM-DD"
    end_date      : str   "YYYY-MM-DD"
    username      : str   exact username
    activity_type : str   one of the ENUM values
"""

import pandas as pd
from .db import get_connection


def _build_where(filters: dict) -> tuple[str, list]:
    conditions, params = [], []

    if filters.get("start_date"):
        conditions.append("ua.login_date >= %s")
        params.append(filters["start_date"])

    if filters.get("end_date"):
        conditions.append("ua.login_date <= %s")
        params.append(filters["end_date"])

    if filters.get("username"):
        conditions.append("u.username = %s")
        params.append(filters["username"])

    if filters.get("activity_type"):
        conditions.append("ua.activity_type = %s")
        params.append(filters["activity_type"])

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    return where, params


def get_activity_data(filters: dict | None = None) -> pd.DataFrame:
    """
    Return raw activity rows matching filters.

    Columns: activity_id, user_id, username, full_name,
             login_date, login_time, activity_type,
             session_duration, ip_address
    """
    filters = filters or {}
    where, params = _build_where(filters)

    sql = f"""
        SELECT
            ua.activity_id,
            u.user_id,
            u.username,
            u.full_name,
            ua.login_date,
            ua.login_time,
            ua.activity_type,
            ua.session_duration,
            ua.ip_address
        FROM  user_activity ua
        JOIN  users         u  ON u.user_id = ua.user_id
        {where}
        ORDER BY ua.login_date DESC, ua.login_time DESC
    """

    conn = get_connection()
    try:
        df = pd.read_sql(sql, conn, params=tuple(params))
    finally:
        conn.close()

    df["login_date"] = pd.to_datetime(df["login_date"])
    return df


def get_activity_summary(filters: dict | None = None) -> dict:
    """
    Return aggregated KPIs + breakdowns for the User Activity Report.

    Returns
    -------
    {
        "total_active_users":  int,
        "total_sessions":      int,
        "avg_session_minutes": float,
        "by_user":             pd.DataFrame,  # username, full_name, login_count, avg_session
        "by_activity_type":    pd.DataFrame,  # activity_type, count
        "by_date":             pd.DataFrame,  # login_date, login_count
        "top_users":           pd.DataFrame,  # top 10 by login_count
    }
    """
    df = get_activity_data(filters)

    if df.empty:
        empty = pd.DataFrame()
        return {
            "total_active_users":  0,
            "total_sessions":      0,
            "avg_session_minutes": 0.0,
            "by_user":             empty,
            "by_activity_type":    empty,
            "by_date":             empty,
            "top_users":           empty,
        }

    login_df = df[df["activity_type"] == "Login"]

    by_user = (
        df.groupby(["username", "full_name"], as_index=False)
        .agg(login_count=("activity_id", "count"),
             avg_session=("session_duration", "mean"))
        .sort_values("login_count", ascending=False)
    )
    by_user["avg_session"] = by_user["avg_session"].round(1)

    by_activity = (
        df.groupby("activity_type", as_index=False)
        .agg(count=("activity_id", "count"))
        .sort_values("count", ascending=False)
    )

    by_date = (
        df.groupby("login_date", as_index=False)
        .agg(login_count=("activity_id", "count"))
        .sort_values("login_date")
    )

    sessions = login_df["session_duration"].dropna()
    avg_session = float(sessions.mean()) if not sessions.empty else 0.0

    return {
        "total_active_users":  int(df["user_id"].nunique()),
        "total_sessions":      int(len(login_df)),
        "avg_session_minutes": round(avg_session, 1),
        "by_user":             by_user,
        "by_activity_type":    by_activity,
        "by_date":             by_date,
        "top_users":           by_user.head(10),
    }


def get_available_filters() -> dict:
    """Return distinct values for each User Activity filter dropdown."""
    sql_users = "SELECT username FROM users ORDER BY username"
    sql_types = """
        SELECT DISTINCT activity_type
        FROM user_activity
        ORDER BY activity_type
    """

    conn = get_connection()
    try:
        usernames = pd.read_sql(sql_users, conn)["username"].tolist()
        activity_types = pd.read_sql(sql_types, conn)["activity_type"].tolist()
    finally:
        conn.close()

    return {"start_date": "All data on or after the start date", "end_date": "All data up to the end date", "usernames": usernames, "activity_types": activity_types}
