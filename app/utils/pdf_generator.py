from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


def generate_pdf(topic: str, report: dict, filename="report.pdf"):
    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()

    content = []

    content.append(Paragraph(f"<b>{topic}</b>", styles["Title"]))
    content.append(Spacer(1, 12))

    for section, text in report.items():
        content.append(Paragraph(f"<b>{section}</b>", styles["Heading2"]))
        content.append(Spacer(1, 8))

        clean_text = text.replace("\n", "<br/>")  
        content.append(Paragraph(clean_text, styles["BodyText"]))

        content.append(Spacer(1, 12))

    doc.build(content)

    return filename