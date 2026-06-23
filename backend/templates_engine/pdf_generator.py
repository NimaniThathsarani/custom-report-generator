import io
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_pdf_report(report_type, summary_data, df_data):
    file_stream = io.BytesIO()
    # Landscape orientation fits tables better
    doc = SimpleDocTemplate(file_stream, pagesize=landscape(letter), rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors.HexColor("#1F4E78"),
        spaceAfter=15
    )
    section_style = ParagraphStyle(
        'SectionStyle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor("#2C3E50"),
        spaceBefore=10,
        spaceAfter=10
    )
    normal_style = styles['Normal']
    
    # 1. Main Title
    story.append(Paragraph(f"Custom Report: {report_type.title()}", title_style))
    story.append(Spacer(1, 10))
    
    # 2. Summary KPI Section
    if summary_data:
        story.append(Paragraph("Executive Summary", section_style))
        summary_table_data = []
        for key, val in summary_data.items():
            display_key = key.replace('_', ' ').title()
            summary_table_data.append([Paragraph(f"<b>{display_key}</b>", normal_style), str(val)])
            
        summary_table = Table(summary_table_data, colWidths=[150, 150])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F2F4F7")),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#D1D5DB")),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
    # 3. Data Table Section
    if not df_data.empty:
        story.append(Paragraph("Detailed Report Data", section_style))
        
        # Prepare headers and body rows
        headers = [col.replace('_', ' ').title() for col in df_data.columns]
        pdf_table_data = [headers]
        
        for _, row in df_data.iterrows():
            pdf_table_data.append([str(val) if val is not None else "" for val in row.values])
            
        # Dynamically calculate columns widths based on total available width (~730 points for landscape letter)
        num_cols = len(headers)
        col_width = 730 / num_cols
        
        data_table = Table(pdf_table_data, colWidths=[col_width]*num_cols, repeatRows=1)
        data_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2C3E50")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#FFFFFF")),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E5E7EB")),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,1), (-1,-1), 9),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F9FAFB")]), # Alternating rows
        ]))
        story.append(data_table)
        
    doc.build(story)
    file_stream.seek(0)
    return file_stream