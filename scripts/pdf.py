from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import io


def generate_pdf(test_data):
    font_path = "./scripts/fonts/ArialRegular.ttf"
    pdfmetrics.registerFont(TTFont("Arial", font_path))
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle("TitleStyle", parent=styles["Title"], fontName="Arial", fontSize=16, spaceAfter=10, leading=20, textColor=colors.black)
    subtitle_style = ParagraphStyle("SubtitleStyle", parent=styles["Normal"], fontName="Arial", fontSize=12, spaceAfter=5, leading=15, textColor=colors.black)
    table_text_style = ParagraphStyle("TableTextStyle", parent=styles["Normal"], fontName="Arial", fontSize=12, leading=14)
    
    elements.append(Paragraph(f"{test_data[0][2]}", title_style))
    elements.append(Paragraph(f"Тест нәтижесі: {test_data[0][4]}",subtitle_style))
    elements.append(Spacer(2, 20))
    elements.append(Paragraph(f"Тесті өту күні: {test_data[0][5]}", subtitle_style))
    elements.append(Spacer(2, 20))
    
    table_data = [["№", "Сұрақ", "Берілген жауап"]]
    table_data += [[str(record[6]), Paragraph(record[7], table_text_style), Paragraph(record[8], table_text_style)] for record in test_data]
    
    table = Table(table_data, colWidths=[30, 350, 100])
    
    style = TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Arial"),
        ("FONTSIZE", (0, 0), (-1, -1), 12),
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
    ])
    
    table.setStyle(style)
    elements.append(table)
    doc.build(elements)
    
    buffer.seek(0)
    return buffer
