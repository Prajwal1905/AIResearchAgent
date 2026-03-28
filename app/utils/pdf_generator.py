from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from xml.sax.saxutils import escape
import re


def clean_html(text):
    text = text.replace("<br>", "\n").replace("<br/>", "\n")
    text = text.replace("&nbsp;", " ")
    return text


def remove_urls(text):
    return re.sub(r"https?://\S+", "", text)


def format_markdown(text):
    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
    return text



def clean_ai_artifacts(text):
    text = re.sub(r"Correction:.*", "", text)
    text = re.sub(r"Clarification:.*", "", text)
    text = re.sub(r"Reference data:.*", "", text)
    return text


def convert_citations(text, references):
    def repl(match):
        num = int(match.group(1))

        ref = next((r for r in references if r.get("id") == num), None)

        if ref:
            url = ref.get("url", "#")
            return f'<link href="{url}"><u>[{num}]</u></link>'

        return match.group(0)

    return re.sub(r"\[(\d+)\]", repl, text)


def process_text(text, styles, references, link_style):
    elements = []
    lines = text.split("\n")

    buffer = []
    i = 0

    while i < len(lines):
        line = lines[i]

        
        line = clean_ai_artifacts(line)

        
        if "|" in line:
            if buffer:
                combined = " ".join(buffer)
                combined = remove_urls(combined)
                combined = clean_html(combined)
                combined = convert_citations(combined, references)

                elements.append(Paragraph(combined, link_style))
                elements.append(Spacer(1, 10))
                buffer = []

            table_data = []

            while i < len(lines) and "|" in lines[i]:
                row = [cell.strip() for cell in lines[i].split("|") if cell.strip()]

                if row and not all(set(cell) <= {"-"} for cell in row):
                    table_data.append(row)

                i += 1

            wrapped_data = []
            for row in table_data:
                wrapped_row = []
                for cell in row:
                    cell = clean_ai_artifacts(cell)
                    cell = remove_urls(cell)
                    cell = clean_html(cell)
                    cell = convert_citations(cell, references)
                    cell = format_markdown(cell)

                    wrapped_row.append(Paragraph(cell, styles["BodyText"]))
                wrapped_data.append(wrapped_row)

            if wrapped_data:
                col_count = len(wrapped_data[0])
                page_width = A4[0] - 100
                col_widths = [page_width / col_count] * col_count

                table = Table(
                    wrapped_data,
                    colWidths=col_widths,
                    repeatRows=1,
                    splitByRow=1
                )

                table.setStyle(TableStyle([
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]))

                elements.append(table)
                elements.append(Spacer(1, 12))

            continue

        
        elif line.startswith("### "):
            heading = clean_html(format_markdown(escape(line.replace("### ", ""))))
            elements.append(Paragraph(f"<b>{heading}</b>", styles["Heading3"]))
            elements.append(Spacer(1, 8))

        elif line.startswith("#### "):
            heading = clean_html(format_markdown(escape(line.replace("#### ", ""))))
            elements.append(Paragraph(f"<b>{heading}</b>", styles["Heading4"]))
            elements.append(Spacer(1, 6))

       
        else:
            line = remove_urls(line)
            line = clean_html(line)

            line_with_links = convert_citations(line, references)
            formatted_line = format_markdown(line_with_links)

            if formatted_line.strip().startswith("- "):
                formatted_line = f"• {formatted_line.strip()[2:]}"

            buffer.append(formatted_line)

        i += 1

    # flush remaining buffer
    if buffer:
        combined = " ".join(buffer)
        combined = remove_urls(combined)
        combined = clean_html(combined)
        combined = convert_citations(combined, references)

        elements.append(Paragraph(combined, link_style))

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

    link_style = ParagraphStyle(
        'LinkStyle',
        parent=styles['BodyText'],
        linkColor=colors.blue,
    )

    content = []

    # Title
    content.append(Paragraph(f"<b>{escape(topic)}</b>", styles["Title"]))
    content.append(Spacer(1, 16))

    # Author
    content.append(Paragraph("AI Research Assistant", styles["Normal"]))
    content.append(Spacer(1, 20))

    references = report.get("references", [])

    # Sections
    for i, (section, text) in enumerate(report.items(), start=1):
        if not isinstance(text, str):
            continue

        section_title = f"{i}. {section}"

        content.append(Paragraph(f"<b>{escape(section_title)}</b>", styles["Heading2"]))
        content.append(Spacer(1, 8))

        processed_elements = process_text(text, styles, references, link_style)
        content.extend(processed_elements)

        content.append(Spacer(1, 12))

   
    if references:
        content.append(Paragraph("<b>References</b>", styles["Heading2"]))
        content.append(Spacer(1, 10))

        for ref in references:
            ref_text = f"[{ref['id']}] {ref.get('title')}"

            if ref.get("url"):
                ref_text += f' <link href="{ref["url"]}">{ref["url"]}</link>'

            content.append(Paragraph(ref_text, styles["BodyText"]))
            content.append(Spacer(1, 6))

    doc.build(content)

    return filename