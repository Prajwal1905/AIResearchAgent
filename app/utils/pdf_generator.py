from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from xml.sax.saxutils import escape
import re


def clean_text(text):
    text = text.replace("<br>", "\n").replace("<br/>", "\n")
    text = text.replace("&nbsp;", " ")
    # remove bare URLs from body text
    text = re.sub(r"https?://\S+", "", text)
    return text


def format_bold(text):
    return re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)


def convert_citations_to_links(text, references):
    def repl(match):
        num = int(match.group(1))
        ref = next((r for r in references if r.get("id") == num), None)
        if ref and ref.get("url"):
            url = escape(ref.get("url", "#"))
            return f'<link href="{url}" color="blue"><u>[{num}]</u></link>'
        return f"[{num}]"

    return re.sub(r"\[(\d+)\]", repl, text)


def process_paragraph(line, references, link_style):
    line = clean_text(line)
    line = convert_citations_to_links(line, references)
    line = format_bold(line)

    if line.strip().startswith("- "):
        line = f"• {line.strip()[2:]}"

    return Paragraph(line, link_style)


def generate_pdf(topic: str, report: dict, filename="research_paper.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=60,
        bottomMargin=60
    )

    styles = getSampleStyleSheet()

    # body style
    body_style = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontSize=11,
        leading=16,
        spaceAfter=8,
        alignment=TA_JUSTIFY,
    )

    
    link_style = ParagraphStyle(
        "LinkStyle",
        parent=body_style,
        textColor=colors.black,
    )

    heading1_style = ParagraphStyle(
        "H1",
        parent=styles["Heading1"],
        fontSize=16,
        spaceAfter=6,
        spaceBefore=14,
    )

    heading2_style = ParagraphStyle(
        "H2",
        parent=styles["Heading2"],
        fontSize=13,
        spaceAfter=6,
        spaceBefore=12,
    )

    content = []
    references = report.get("references", [])

    # title
    content.append(Paragraph(f"<b>{escape(topic)}</b>", styles["Title"]))
    content.append(Spacer(1, 6))
    content.append(Paragraph("AI Research Assistant", styles["Normal"]))
    content.append(Spacer(1, 24))

    section_number = 1

    for section, text in report.items():
        if section == "references":
            continue

        if not isinstance(text, str):
            continue

        # section heading
        content.append(Paragraph(f"<b>{section_number}. {escape(section)}</b>", heading1_style))
        content.append(Spacer(1, 8))
        section_number += 1

        lines = text.split("\n")
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            if not line:
                content.append(Spacer(1, 6))
                i += 1
                continue

            # handle markdown tables
            if "|" in line:
                table_data = []
                while i < len(lines) and "|" in lines[i]:
                    row = [cell.strip() for cell in lines[i].split("|") if cell.strip()]
                    if row and not all(set(cell) <= {"-"} for cell in row):
                        table_data.append(row)
                    i += 1

                if table_data:
                    col_count = max(len(row) for row in table_data)
                    page_width = A4[0] - 100
                    col_widths = [page_width / col_count] * col_count

                    wrapped = []
                    for row in table_data:
                        wrapped_row = []
                        for cell in row:
                            cell = clean_text(cell)
                            cell = convert_citations_to_links(cell, references)
                            cell = format_bold(cell)
                            wrapped_row.append(Paragraph(cell, body_style))
                        wrapped.append(wrapped_row)

                    table = Table(wrapped, colWidths=col_widths, repeatRows=1)
                    table.setStyle(TableStyle([
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2d2d2d")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
                    ]))
                    content.append(table)
                    content.append(Spacer(1, 12))
                continue

            # subheadings
            if line.startswith("### "):
                heading = escape(line.replace("### ", ""))
                content.append(Paragraph(f"<b>{heading}</b>", heading2_style))

            elif line.startswith("## "):
                heading = escape(line.replace("## ", ""))
                content.append(Paragraph(f"<b>{heading}</b>", heading1_style))

            else:
                # normal paragraph with citations as clickable links
                para = process_paragraph(line, references, link_style)
                content.append(para)
                content.append(Spacer(1, 4))

            i += 1

        content.append(Spacer(1, 16))

    # references section
    if references:
        content.append(Paragraph("<b>References</b>", heading1_style))
        content.append(Spacer(1, 8))

        for ref in references:
            title = escape(ref.get("title") or "Untitled")
            url = ref.get("url", "")
            ref_id = ref.get("id")

            if url:
                ref_line = f'[{ref_id}] {title} — <link href="{escape(url)}" color="blue"><u>{escape(url)}</u></link>'
            else:
                ref_line = f"[{ref_id}] {title}"

            content.append(Paragraph(ref_line, link_style))
            content.append(Spacer(1, 6))

    doc.build(content)
    return filename
