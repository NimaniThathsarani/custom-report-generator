from flask import Blueprint, request, send_file, jsonify
import pandas as pd

# Import data fetching and summary utilities from the core models module
from backend.models import (
    get_sales_data, get_sales_summary,
    get_activity_data, get_activity_summary,
    get_inventory_data, get_inventory_summary
)

# Import report generation engines
from backend.templates_engine.excel_generator import generate_excel_report
from backend.templates_engine.pdf_generator import generate_pdf_report

report_bp = Blueprint('report_bp', __name__)

@report_bp.route('/api/generate-report', methods=['POST'])
def generate_report_endpoint():
    try:
        data = request.json or {}
        report_type = data.get('report_type')  # Supported: 'sales', 'activity', 'inventory'
        export_format = data.get('export_format', 'excel').lower() # Supported: 'excel', 'pdf'
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

        # Process the data through the designated template engine format
        if export_format == 'excel':
            file_stream = generate_excel_report(report_type, summary_data, df_data)
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            filename = f"{report_type}_report.xlsx"
        elif export_format == 'pdf':
            file_stream = generate_pdf_report(report_type, summary_data, df_data)
            mimetype = 'application/pdf'
            filename = f"{report_type}_report.pdf"
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