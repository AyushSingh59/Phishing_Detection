import json
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from urllib.parse import urlparse

def normalize_url(url):
    from ml_utils import normalize_url as ml_normalize
    return ml_normalize(url)


def is_valid_url(url):
    from ml_utils import is_valid_url as ml_valid
    return ml_valid(url)


def safe_api_key(provided_key, expected_key):
    if not expected_key:
        return True
    return provided_key == expected_key


def build_scan_steps():
    return [
        "Validating URL input",
        "Extracting URL features",
        "Performing ML prediction",
        "Collecting WHOIS and SSL intelligence",
        "Checking VirusTotal and Safe Browsing",
        "Calculating risk score",
        "Saving scan history",
    ]


def create_pdf_report(records, summary):
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, topMargin=0.5 * 72, bottomMargin=0.5 * 72)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        fontSize=22,
        textColor=colors.HexColor("#0b3d91"),
        spaceAfter=18,
    )
    normal = styles["BodyText"]
    elements = []
    elements.append(Paragraph("Phishing Detection Scan Report", title_style))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal))
    elements.append(Spacer(1, 12))

    if summary:
        summary_items = [f"{key}: {value}" for key, value in summary.items() if value is not None]
        elements.append(Paragraph("<b>Summary</b>", styles["Heading3"]))
        for item in summary_items:
            elements.append(Paragraph(item, normal))
        elements.append(Spacer(1, 12))

    table_data = [["URL", "Result", "Confidence", "Risk", "Timestamp"]]
    for record in records:
        table_data.append([
            record["url"],
            record["result"],
            f"{record['confidence']}%",
            f"{record['risk_score']}%",
            record["timestamp"],
        ])

    table = Table(table_data, repeatRows=1, colWidths=[190, 90, 70, 70, 100])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0b3d91")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
    ]))
    elements.append(table)
    doc.build(elements)
    pdf_buffer.seek(0)
    return pdf_buffer


def safe_json_load(text):
    try:
        return json.loads(text)
    except Exception:
        return {}
