from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from xml.sax.saxutils import escape
import re


# MARKDOWN FORMATTER
def format_markdown(text):
    # Convert **bold** → <b>bold</b>
    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
    return text

def process_text(text, styles,references):
    elements = []
    lines = text.split("\n")

    buffer = []
    i = 0

    while i < len(lines):
        line = lines[i]

        #  TABLE DETECTION 
        if "|" in line:
            if buffer:
                elements.append(Paragraph("<br/>".join(buffer), styles["BodyText"]))
                elements.append(Spacer(1, 10))
                buffer = []

            table_data = []

            while i < len(lines) and "|" in lines[i]:
                row = [cell.strip() for cell in lines[i].split("|") if cell.strip()]

                
                if row and not all(set(cell) <= {"-"} for cell in row):
                    table_data.append(row)

                i += 1

            # Wrap cells
            wrapped_data = []
            for row in table_data:
                wrapped_row = [
                    Paragraph(format_markdown(escape(cell)), styles["BodyText"])
                    for cell in row
                ]
                wrapped_data.append(wrapped_row)

            # Column width fix
            col_count = len(wrapped_data[0])
            page_width = A4[0] - 100
            col_widths = [page_width / col_count] * col_count

            # Create table
            table = Table(
                wrapped_data,
                colWidths=col_widths,
                repeatRows=1,
                splitByRow=1
            )

            # Style table
            table.setStyle(TableStyle([
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("WORDWRAP", (0, 0), (-1, -1), "CJK"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))

            elements.append(table)
            elements.append(Spacer(1, 12))

            continue

        
        elif line.startswith("### "):
            if buffer:
                elements.append(Paragraph("<br/>".join(buffer), styles["BodyText"]))
                elements.append(Spacer(1, 10))
                buffer = []

            heading = format_markdown(escape(line.replace("### ", "")))
            elements.append(Paragraph(f"<b>{heading}</b>", styles["Heading3"]))
            elements.append(Spacer(1, 8))

        elif line.startswith("#### "):
            if buffer:
                elements.append(Paragraph("<br/>".join(buffer), styles["BodyText"]))
                elements.append(Spacer(1, 10))
                buffer = []

            heading = format_markdown(escape(line.replace("#### ", "")))
            elements.append(Paragraph(f"<b>{heading}</b>", styles["Heading4"]))
            elements.append(Spacer(1, 6))

        
        else:
            formatted_line = format_markdown(escape(line))
            buffer.append(formatted_line)

        i += 1

    # Remaining text
    if buffer:
        elements.append(Paragraph("<br/>".join(buffer), styles["BodyText"]))

    return elements


def generate_pdf(topic: str, report: dict, filename="research_paper.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=50,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()

    # Optional font tuning
    styles["Heading3"].fontSize = 14
    styles["Heading4"].fontSize = 12

    content = []

    # Title
    content.append(Paragraph(f"<b>{escape(topic)}</b>", styles["Title"]))
    content.append(Spacer(1, 16))

    # Author
    content.append(Paragraph("AI Research Assistant", styles["Normal"]))
    content.append(Spacer(1, 20))

    # Sections
    for i, (section, text) in enumerate(report.items(), start=1):
        section_title = f"{i}. {section}"

        content.append(Paragraph(f"<b>{escape(section_title)}</b>", styles["Heading2"]))
        content.append(Spacer(1, 8))

        processed_elements = process_text(text, styles,report.get("References", []))
        content.extend(processed_elements)

        content.append(Spacer(1, 12))

    # Build PDF
    doc.build(content)

    return filename