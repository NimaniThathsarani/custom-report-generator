from flask import Blueprint, request, send_file, jsonify
from datetime import datetime
import pandas as pd

# Import data fetching and summary utilities from the core models module
from backend.models import (
    get_sales_data, get_sales_summary, get_sales_filters,
    get_activity_data, get_activity_summary, get_activity_filters,
    get_inventory_data, get_inventory_summary, get_inventory_filters
)

# Import report generation engines
from backend.templates_engine.excel_generator import generate_excel_report
from backend.templates_engine.pdf_generator import generate_pdf_report

report_bp = Blueprint('report_bp', __name__)


@report_bp.route('/api/generate-report', methods=['POST'])
def generate_report_endpoint():
    try:
        data = request.json or {}
        # Supported: 'sales', 'activity', 'inventory'
        report_type = data.get('report_type')
        # Supported: 'excel', 'pdf'
        export_format = data.get('export_format', 'excel').lower()
        filters = data.get('filters', {})

        if not report_type:
            return jsonify({"error": "Missing 'report_type' parameter"}), 400

        summary_data = {}
        df_data = pd.DataFrame()

        # Dynamically fetch records and summaries based on the requested report type
        if report_type == 'sales':
            summary_data = get_sales_summary(filters)
            df_data = get_sales_data(filters)
        elif report_type == 'activity':
            summary_data = get_activity_summary(filters)
            df_data = get_activity_data(filters)
        elif report_type == 'inventory':
            summary_data = get_inventory_summary(filters)
            df_data = get_inventory_data(filters)
        else:
            return jsonify({"error": f"Invalid report type: {report_type}"}), 400

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
        return send_file(
            file_stream,
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )

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
