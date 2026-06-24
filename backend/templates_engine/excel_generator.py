import io
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side


def generate_excel_report(report_type, summary_data, df_data):
    wb = Workbook()
    ws = wb.active
    ws.title = f"{report_type} Report"

    # Styles
    title_font = Font(name="Arial", size=16, bold=True, color="FFFFFF")
    header_font = Font(name="Arial", size=11, bold=True, color="FFFFFF")
    kpi_font = Font(name="Arial", size=11, bold=True, color="000000")
    bold_font = Font(name="Arial", size=10, bold=True)
    normal_font = Font(name="Arial", size=10)

    title_fill = PatternFill(start_color="1F4E78",
                             end_color="1F4E78", fill_type="solid")
    header_fill = PatternFill(start_color="2C3E50",
                              end_color="2C3E50", fill_type="solid")
    kpi_fill = PatternFill(start_color="D9E1F2",
                           end_color="D9E1F2", fill_type="solid")

    thin_border = Border(
        left=Side(style='thin', color='BFBFBF'),
        right=Side(style='thin', color='BFBFBF'),
        top=Side(style='thin', color='BFBFBF'),
        bottom=Side(style='thin', color='BFBFBF')
    )

    # 1. Title Block
    ws.merge_cells("A1:H2")
    ws["A1"] = f"CUSTOM REPORT: {report_type.upper()}"
    ws["A1"].font = title_font
    ws["A1"].fill = title_fill
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")

    current_row = 4

    # 2. KPI / Summary Section
    if summary_data:
        ws.cell(row=current_row, column=1,
                value="Key Performance Indicators (KPIs)").font = bold_font
        current_row += 1

        for key, value in summary_data.items():
            # Format keys nicely (e.g., total_revenue -> Total Revenue)
            display_key = key.replace('_', ' ').title()

            ws.cell(row=current_row, column=1,
                    value=display_key).font = normal_font
            ws.cell(row=current_row, column=1).fill = kpi_fill
            ws.cell(row=current_row, column=1).border = thin_border

            val_cell = ws.cell(row=current_row, column=2, value=value)
            val_cell.font = kpi_font
            val_cell.fill = kpi_fill
            val_cell.border = thin_border
            if isinstance(value, (int, float)):
                val_cell.number_format = '#,##0.00' if isinstance(
                    value, float) else '#,##0'

            current_row += 1
        current_row += 2  # Space

    # 3. Data Table Section
    if not df_data.empty:
        ws.cell(row=current_row, column=1,
                value="Detailed Data Records").font = bold_font
        current_row += 1

        # Table Headers
        headers = [col.replace('_', ' ').title() for col in df_data.columns]
        for col_idx, header in enumerate(headers, 1):
            cell = ws.cell(row=current_row, column=col_idx, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center")
            cell.border = thin_border

        current_row += 1

        # Table Data
        for row_idx, row_data in df_data.iterrows():
            for col_idx, value in enumerate(row_data, 1):
                cell = ws.cell(row=current_row, column=col_idx, value=value)
                cell.font = normal_font
                cell.border = thin_border

                # Check data types for proper formatting
                if isinstance(value, (int, float)):
                    cell.number_format = '#,##0.00' if isinstance(
                        value, float) else '#,##0'
                    cell.alignment = Alignment(horizontal="right")

            current_row += 1

    # Auto-fit column widths
    for col in ws.columns:
        max_len = 0
        for cell in col:
            val_str = str(cell.value or '')
            if len(val_str) > max_len:
                max_len = len(val_str)

        # Use cell.column index instead of .column_letter property to prevent MergedCell AttributeErrors
        col_idx = col[0].column
        col_letter = get_column_letter(col_idx)
        ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

    # Save to BytesIO buffer
    file_stream = io.BytesIO()
    wb.save(file_stream)
    file_stream.seek(0)
    return file_stream
