"""
backend/routes/report_routes.py
================================
Flask Blueprint exposing all report-related API endpoints.

Endpoints
---------
POST /api/generate-report
    Body (JSON):
    {
        "report_type":   "sales" | "user_activity" | "inventory",
        "export_format": "excel" | "pdf",
        "filters": {
            // Sales      : start_date, end_date, category, region
            // Activity   : start_date, end_date, username, activity_type
            // Inventory  : category, warehouse_location
        }
    }
    Response: file attachment (.xlsx or .pdf)

GET /api/filters/<report_type>
    Returns available filter values for the given report type.
    Response:
    {
        "report_type": "sales",
        "filters": { "categories": [...], "regions": [...], ... }
    }

GET /api/report-types
    Returns the list of supported report types and their filter keys.
"""

from flask import Blueprint, request, send_file, jsonify
from datetime import datetime
import pandas as pd

# Data-access helpers
from backend.models import (
<<<<<<< Updated upstream
    get_sales_data, get_sales_summary, get_sales_filters,
    get_activity_data, get_activity_summary, get_activity_filters,
    get_inventory_data, get_inventory_summary, get_inventory_filters
=======
    get_sales_data,      get_sales_summary,      get_sales_filters,
    get_activity_data,   get_activity_summary,   get_activity_filters,
    get_inventory_data,  get_inventory_summary,  get_inventory_filters,
>>>>>>> Stashed changes
)

# Template engines
from backend.templates_engine.excel_generator import generate_excel_report
from backend.templates_engine.pdf_generator   import generate_pdf_report

report_bp = Blueprint("report_bp", __name__)

<<<<<<< Updated upstream

@report_bp.route('/api/generate-report', methods=['POST'])
=======
# ── Supported report types (used for validation) ─────────────────────────────
_REPORT_TYPES = {"sales", "user_activity", "inventory"}


# ---------------------------------------------------------------------------
# POST /api/generate-report
# ---------------------------------------------------------------------------
@report_bp.route("/api/generate-report", methods=["POST"])
>>>>>>> Stashed changes
def generate_report_endpoint():
    """
    Generate and download a report file.

    Expected JSON body:
    {
        "report_type":   "sales",
        "export_format": "excel",
        "filters": { "start_date": "2026-01-01", "end_date": "2026-06-30" }
    }
    """
    try:
<<<<<<< Updated upstream
        data = request.json or {}
        # Supported: 'sales', 'activity', 'inventory'
        report_type = data.get('report_type')
        # Supported: 'excel', 'pdf'
        export_format = data.get('export_format', 'excel').lower()
        filters = data.get('filters', {})
=======
        data          = request.json or {}
        report_type   = data.get("report_type", "").strip().lower()
        export_format = data.get("export_format", "excel").strip().lower()
        filters       = data.get("filters", {})
>>>>>>> Stashed changes

        # ── Validate inputs ──────────────────────────────────────────────────
        if not report_type:
            return jsonify({"error": "Missing required field: 'report_type'"}), 400
        if report_type not in _REPORT_TYPES:
            return jsonify({
                "error": f"Invalid report_type '{report_type}'. "
                         f"Supported values: {sorted(_REPORT_TYPES)}"
            }), 400
        if export_format not in {"excel", "pdf"}:
            return jsonify({
                "error": f"Invalid export_format '{export_format}'. "
                         "Supported values: 'excel', 'pdf'"
            }), 400

        # ── Fetch data ───────────────────────────────────────────────────────
        if report_type == "sales":
            summary = get_sales_summary(filters)
            df      = get_sales_data(filters)
        elif report_type == "user_activity":
            summary = get_activity_summary(filters)
            df      = get_activity_data(filters)
        else:  # inventory
            summary = get_inventory_summary(filters)
            df      = get_inventory_data(filters)

        # ── Render ───────────────────────────────────────────────────────────
        if export_format == "excel":
            file_stream = generate_excel_report(report_type, summary, df)
            mimetype    = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename    = f"{report_type}_report.xlsx"
        else:
            file_stream = generate_pdf_report(report_type, summary, df)
            mimetype    = "application/pdf"
            filename    = f"{report_type}_report.pdf"

<<<<<<< Updated upstream
        # This removes nested DataFrames so OpenPyXL only gets clean metrics (numbers/strings)
        if isinstance(summary_data, dict):
            summary_data = {
                key: value for key, value in summary_data.items()
                if not isinstance(value, pd.DataFrame)
            }

        # Generate a standardized timestamp string (YYYYMMDD_HHMMSS)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

        # Process the data through the designated template engine format
        if export_format == 'excel':
            file_stream = generate_excel_report(
                report_type, summary_data, df_data)
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            filename = f"{report_type}_report_{timestamp}.xlsx"
        elif export_format == 'pdf':
            file_stream = generate_pdf_report(
                report_type, summary_data, df_data)
            mimetype = 'application/pdf'
            filename = f"{report_type}_report_{timestamp}.pdf"
        else:
            return jsonify({"error": "Invalid format. Supported formats are 'excel' or 'pdf'"}), 400

        # Return the generated file stream as a downloadable attachment
=======
>>>>>>> Stashed changes
        return send_file(
            file_stream,
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename,
        )

<<<<<<< Updated upstream
    except Exception as e:
        return jsonify({"error": f"Server Error: {str(e)}"}), 500


@report_bp.route('/api/filters/<report_type>', methods=['GET'])
def get_available_filters_endpoint(report_type):
    try:
        filters = {}
        if report_type == 'sales':
            filters = get_sales_filters()
        elif report_type == 'activity':
            filters = get_activity_filters()
        elif report_type == 'inventory':
            filters = get_inventory_filters()
        else:
            return jsonify({"error": f"Invalid report type {report_type}. Supported types are 'sales', 'activity', and 'inventory'."}), 400

        return jsonify(filters), 200

    except Exception as e:
        return jsonify({"error": f"Server Error: {str(e)}"}), 500
=======
    except Exception as exc:
        return jsonify({"error": f"Server error: {str(exc)}"}), 500


# ---------------------------------------------------------------------------
# GET /api/filters/<report_type>
# ---------------------------------------------------------------------------
@report_bp.route("/api/filters/<report_type>", methods=["GET"])
def get_filters(report_type: str):
    """
    Return available filter dropdown values for the requested report type.

    Example response for 'sales':
    {
        "report_type": "sales",
        "filters": {
            "start_date": "All data on or after the start date",
            "end_date":   "All data up to the end date",
            "categories": ["Clothing", "Electronics", ...],
            "regions":    ["Central Province", "Western Province", ...]
        }
    }
    """
    report_type = report_type.strip().lower()

    if report_type not in _REPORT_TYPES:
        return jsonify({
            "error": f"Invalid report_type '{report_type}'. "
                     f"Supported values: {sorted(_REPORT_TYPES)}"
        }), 400

    try:
        if report_type == "sales":
            filter_values = get_sales_filters()
        elif report_type == "user_activity":
            filter_values = get_activity_filters()
        else:
            filter_values = get_inventory_filters()

        return jsonify({
            "report_type": report_type,
            "filters":     filter_values,
        })

    except Exception as exc:
        return jsonify({"error": f"Server error: {str(exc)}"}), 500


# ---------------------------------------------------------------------------
# GET /api/report-types
# ---------------------------------------------------------------------------
@report_bp.route("/api/report-types", methods=["GET"])
def list_report_types():
    """
    Return metadata about every supported report type.
    Useful for Group 3 / Group 4 to dynamically build the UI.
    """
    return jsonify({
        "report_types": [
            {
                "id":          "sales",
                "label":       "Sales Report",
                "description": "Revenue, orders, and regional/product breakdowns.",
                "filter_keys": ["start_date", "end_date", "category", "region"],
                "formats":     ["excel", "pdf"],
            },
            {
                "id":          "user_activity",
                "label":       "User Activity Report",
                "description": "Login frequency, session stats, and activity breakdown.",
                "filter_keys": ["start_date", "end_date", "username", "activity_type"],
                "formats":     ["excel", "pdf"],
            },
            {
                "id":          "inventory",
                "label":       "Inventory Report",
                "description": "Stock levels, low-stock alerts, and warehouse breakdown.",
                "filter_keys": ["category", "warehouse_location"],
                "formats":     ["excel", "pdf"],
            },
        ]
    })
>>>>>>> Stashed changes
