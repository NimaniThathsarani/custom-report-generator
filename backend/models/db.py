"""
backend/models/db.py
====================
MySQL connection pooling using SQLAlchemy (mysqlclient/mysqlconnector).
All query modules import `get_connection()` from here.

Environment variables (set in .env or system):
    DB_HOST     – default: localhost
    DB_PORT     – default: 3306
    DB_USER     – default: root
    DB_PASSWORD – default: (empty)
    DB_NAME     – default: report_generator
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Engine
from sqlalchemy.engine import Connection

load_dotenv()

# Global engine instance acting as our connection pool
_engine: Engine | None = None


def _get_db_url() -> str:
    """Constructs the standard SQLAlchemy connection URI string."""
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "3306")
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "")
    database = os.getenv("DB_NAME", "report_generator")

    # Using mysql+mysqlconnector to match your current underlying package
    return f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4"


def init_pool() -> None:
    """Call once at application startup (app.py)."""
    global _engine
    if _engine is None:
        db_url = _get_db_url()

        # create_engine handles pooling automatically under the hood
        _engine = create_engine(
            db_url,
            pool_size=10,
            max_overflow=5,
            pool_pre_ping=True
        ).execution_options(autocommit=True)


def get_connection() -> Connection:
    """
    Return a connection from the pool.
    Caller is responsible for closing it (use as context manager or
    call .close() in a finally block).

    Returns a SQLAlchemy Connection object compatible with pandas.read_sql.
    """
    global _engine
    if _engine is None:
        init_pool()

    # Returns a connection from the pool boundary
    return _engine.connect()
