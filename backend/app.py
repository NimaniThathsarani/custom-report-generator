"""
backend/app.py
==============
Entry point for the Custom Report Generator Flask application.

Usage (development):
    python -m backend.app

Or via Flask CLI:
    set FLASK_APP=backend.app:create_app
    flask run --port 5000 --debug

Public helper available for Group 3 / Group 4 direct import:
    from backend.app import generate_report
"""

import os
import sys

# Ensure the project root is on sys.path so 'backend.*' imports work
# whether the file is run directly or as a module.
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from flask import Flask
from flask_cors import CORS

from backend.models import init_pool
from backend.routes.report_routes import report_bp


# ---------------------------------------------------------------------------
# Public helper – callable by any group without going through HTTP
# ---------------------------------------------------------------------------

def generate_report(report_type: str, filters: dict | None = None,
                    export_format: str = "excel"):
    """
    Generate a report file and return it as a BytesIO stream.

    Parameters
    ----------
    report_type   : "sales" | "user_activity" | "inventory"
    filters       : dict of filter keys/values (all optional).
                    Sales      – start_date, end_date, category, region
                    Activity   – start_date, end_date, username, activity_type
                    Inventory  – category, warehouse_location
    export_format : "excel" (default) | "pdf"

    Returns
    -------
    io.BytesIO
        Seek position is 0.  Caller may save it or stream it.

    Raises
    ------
    ValueError  if report_type or export_format is invalid.

    Example
    -------
    >>> from backend.app import generate_report
    >>> buf = generate_report("sales",
    ...                       {"start_date": "2026-06-01",
    ...                        "end_date":   "2026-06-30",
    ...                        "region":     "Western Province"},
    ...                       export_format="pdf")
    >>> with open("sales_june.pdf", "wb") as f:
    ...     f.write(buf.read())
    """
    from backend.models import (
        get_sales_data,      get_sales_summary,
        get_activity_data,   get_activity_summary,
        get_inventory_data,  get_inventory_summary,
    )
    from backend.templates_engine.excel_generator import generate_excel_report
    from backend.templates_engine.pdf_generator   import generate_pdf_report

    filters = filters or {}

    # ── fetch data ──────────────────────────────────────────────────────────
    if report_type == "sales":
        summary = get_sales_summary(filters)
        df      = get_sales_data(filters)
    elif report_type == "user_activity":
        summary = get_activity_summary(filters)
        df      = get_activity_data(filters)
    elif report_type == "inventory":
        summary = get_inventory_summary(filters)
        df      = get_inventory_data(filters)
    else:
        raise ValueError(
            f"Unknown report_type '{report_type}'. "
            "Choose from: 'sales', 'user_activity', 'inventory'."
        )

    # ── render ───────────────────────────────────────────────────────────────
    fmt = export_format.lower()
    if fmt == "excel":
        return generate_excel_report(report_type, summary, df)
    elif fmt == "pdf":
        return generate_pdf_report(report_type, summary, df)
    else:
        raise ValueError(
            f"Unknown export_format '{export_format}'. Choose 'excel' or 'pdf'."
        )


# ---------------------------------------------------------------------------
# Flask app factory
# ---------------------------------------------------------------------------

def create_app() -> Flask:
    app = Flask(__name__)

    # Enable CORS so frontend groups can call this API without browser blocks
    CORS(app)

    # Initialise the DB connection pool once at startup
    init_pool()

    # Register all API blueprints
    app.register_blueprint(report_bp)

    # Initialise and start the background scheduler
    from backend.scheduler.scheduler_setup import init_scheduler, start_scheduler, shutdown_scheduler
    import atexit
    init_scheduler(app)
    start_scheduler()
    atexit.register(shutdown_scheduler)

    @app.route("/")
    def index():
        return {
            "message": "Custom Report Generator Backend is running.",
            "version": "1.0.0",
            "endpoints": {
                "POST /api/generate-report": "Generate and download a report",
                "GET  /api/filters/<report_type>": "Fetch available filter values",
                "GET  /api/health": "Health check",
            },
        }

    @app.route("/api/health")
    def health():
        return {"status": "ok"}

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)