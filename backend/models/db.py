"""
backend/models/db.py
====================
MySQL connection pool using mysql-connector-python.
All query modules import `get_connection()` from here.

Environment variables (set in .env or system):
    DB_HOST     – default: localhost
    DB_PORT     – default: 3306
    DB_USER     – default: root
    DB_PASSWORD – default: (empty)
    DB_NAME     – default: custom_report_generator
"""

import os
import mysql.connector
from mysql.connector import pooling

_pool: pooling.MySQLConnectionPool | None = None


def _pool_config() -> dict:
    return {
        "pool_name":    "report_pool",
        "pool_size":    10,
        "host":         os.getenv("DB_HOST",     "localhost"),
        "port":         int(os.getenv("DB_PORT", "3306")),
        "user":         os.getenv("DB_USER",     "root"),
        "password":     os.getenv("DB_PASSWORD", ""),
        "database":     os.getenv("DB_NAME",     "custom_report_generator"),
        "charset":      "utf8mb4",
        "use_unicode":  True,
        "autocommit":   True,
    }


def init_pool() -> None:
    """Call once at application startup (app.py)."""
    global _pool
    if _pool is None:
        _pool = pooling.MySQLConnectionPool(**_pool_config())


def get_connection() -> mysql.connector.MySQLConnection:
    """
    Return a connection from the pool.
    Caller is responsible for closing it (use as context manager or
    call .close() in a finally block).
    """
    global _pool
    if _pool is None:
        init_pool()
    return _pool.get_connection()
