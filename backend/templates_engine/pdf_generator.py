"""
backend/templates_engine/pdf_generator.py
==========================================
Generates a formatted PDF report using ReportLab.

Public API
----------
generate_pdf_report(report_type, summary_data, df_data) -> io.BytesIO

Parameters
----------
report_type  : str             "sales" | "user_activity" | "inventory"
summary_data : dict            Output of get_*_summary() – may contain scalar
                               values AND pandas DataFrames for breakdown tables.
df_data      : pd.DataFrame    Raw detail rows from get_*_data().

Returns
-------
io.BytesIO  with seek position at 0, ready to stream or save.
"""

import io
import pandas as pd
from datetime import datetime

from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, PageBreak, HRFlowable,
)

# ── Colour palette ──────────────────────────────────────────────────────────
_DARK_BLUE  = colors.HexColor("#1F4E78")
_MID_BLUE   = colors.HexColor("#2C3E50")
_LIGHT_BLUE = colors.HexColor("#D9E1F2")
_ACCENT     = colors.HexColor("#2980B9")
_ALT_ROW    = colors.HexColor("#EEF2F8")
_LIGHT_GREY = colors.HexColor("#F2F4F7")
_BORDER     = colors.HexColor("#D1D5DB")
_WHITE      = colors.white


def _df_to_table(df: pd.DataFrame, col_width_total: float,
                 header_bg=_MID_BLUE) -> Table | Paragraph:
    """Convert a DataFrame to a styled ReportLab Table."""
    if df is None or df.empty:
        styles = getSampleStyleSheet()
        return Paragraph("<i>No data available.</i>",
                         ParagraphStyle("nodata", parent=styles["Normal"],
                                        textColor=colors.grey, fontSize=9))

    headers = [col.replace("_", " ").title() for col in df.columns]
    n_cols  = len(headers)
    col_w   = col_width_total / n_cols

    rows = [headers]
    for _, row in df.iterrows():
        formatted = []
        for val in row:
            if hasattr(val, "item"):           # numpy → Python native
                val = val.item()
            if hasattr(val, "strftime"):       # Timestamp → str
                val = val.strftime("%Y-%m-%d")
            if isinstance(val, float):
                val = f"{val:,.2f}"
            elif isinstance(val, int):
                val = f"{val:,}"
            formatted.append(str(val) if val is not None else "")
        rows.append(formatted)

    tbl = Table(rows, colWidths=[col_w] * n_cols, repeatRows=1)
    tbl.setStyle(TableStyle([
        # Header
        ("BACKGROUND",   (0, 0), (-1, 0),  header_bg),
        ("TEXTCOLOR",    (0, 0), (-1, 0),  _WHITE),
        ("FONTNAME",     (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, 0),  9),
        ("BOTTOMPADDING",(0, 0), (-1, 0),  6),
        ("TOPPADDING",   (0, 0), (-1, 0),  6),
        ("ALIGN",        (0, 0), (-1, 0),  "CENTER"),
        # Body
        ("FONTNAME",     (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",     (0, 1), (-1, -1), 8),
        ("ROWBACKGROUNDS",(0,1), (-1, -1), [_WHITE, _ALT_ROW]),
        ("ALIGN",        (0, 1), (-1, -1), "CENTER"),
        ("TOPPADDING",   (0, 1), (-1, -1), 4),
        ("BOTTOMPADDING",(0, 1), (-1, -1), 4),
        # Grid
        ("GRID",         (0, 0), (-1, -1), 0.4, _BORDER),
    ]))
    return tbl


def generate_pdf_report(report_type: str,
                         summary_data: dict,
                         df_data: pd.DataFrame) -> io.BytesIO:
    file_stream = io.BytesIO()
    doc = SimpleDocTemplate(
        file_stream,
        pagesize=landscape(letter),
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    # Available width for tables (landscape letter ≈ 27.9 cm minus margins)
    page_w = landscape(letter)[0] - 3 * cm   # ~24.9 cm ≈ 706 pt

    styles     = getSampleStyleSheet()
    report_label = report_type.replace("_", " ").title()

    title_style = ParagraphStyle(
        "Title",
        parent   = styles["Heading1"],
        fontSize = 22,
        textColor= _DARK_BLUE,
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent    = styles["Normal"],
        fontSize  = 10,
        textColor = colors.grey,
        spaceAfter= 12,
    )
    section_style = ParagraphStyle(
        "Section",
        parent     = styles["Heading2"],
        fontSize   = 13,
        textColor  = _MID_BLUE,
        spaceBefore= 14,
        spaceAfter = 6,
    )

    story = []

    # ── Cover header ────────────────────────────────────────────────────────
    story.append(Paragraph(f"Custom Report: {report_label}", title_style))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%A, %d %B %Y at %H:%M')}",
        subtitle_style,
    ))
    story.append(HRFlowable(width="100%", thickness=1.5,
                             color=_ACCENT, spaceAfter=12))

    # ── KPI scalars ─────────────────────────────────────────────────────────
    scalar_items = {k: v for k, v in summary_data.items()
                    if not isinstance(v, pd.DataFrame)}
    if scalar_items:
        story.append(Paragraph("Executive Summary", section_style))
        kpi_rows = []
        for key, val in scalar_items.items():
            label = key.replace("_", " ").title()
            if isinstance(val, float):
                display = f"{val:,.2f}"
            elif isinstance(val, int):
                display = f"{val:,}"
            else:
                display = str(val)
            kpi_rows.append([
                Paragraph(f"<b>{label}</b>", styles["Normal"]),
                Paragraph(display, styles["Normal"]),
            ])

        kpi_table = Table(kpi_rows, colWidths=[200, 160])
        kpi_table.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), _LIGHT_GREY),
            ("GRID",          (0, 0), (-1, -1), 0.4, _BORDER),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING",   (0, 0), (-1, -1), 8),
            ("ROWBACKGROUNDS",(0, 0), (-1, -1), [_LIGHT_GREY, _WHITE]),
        ]))
        story.append(kpi_table)
        story.append(Spacer(1, 14))

    # ── Breakdown DataFrames ─────────────────────────────────────────────────
    df_items = {k: v for k, v in summary_data.items()
                if isinstance(v, pd.DataFrame)}
    for section_name, section_df in df_items.items():
        story.append(Paragraph(section_name.replace("_", " ").title(), section_style))
        story.append(_df_to_table(section_df, page_w, header_bg=_ACCENT))
        story.append(Spacer(1, 10))

    # ── Detail records (new page) ────────────────────────────────────────────
    if not df_data.empty:
        story.append(PageBreak())
        story.append(Paragraph("Detailed Report Data", section_style))
        story.append(HRFlowable(width="100%", thickness=0.8,
                                 color=_BORDER, spaceAfter=8))
        story.append(_df_to_table(df_data, page_w, header_bg=_MID_BLUE))

    doc.build(story)
    file_stream.seek(0)
    return file_stream