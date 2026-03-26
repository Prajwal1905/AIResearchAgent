from docx import Document
from docx.shared import Pt
import re


#  FORMAT MARKDOWN 
def format_markdown(text):
    # bold
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    return text



def process_text(doc, text):
    lines = text.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i]

        # TABLE 
        if "|" in line:
            table_data = []

            while i < len(lines) and "|" in lines[i]:
                row = [cell.strip() for cell in lines[i].split("|") if cell.strip()]

                # skip ---- row
                if row and not all(set(cell) <= {"-"} for cell in row):
                    table_data.append(row)

                i += 1

            if table_data:
                rows = len(table_data)
                cols = len(table_data[0])

                table = doc.add_table(rows=rows, cols=cols)

                for r in range(rows):
                    for c in range(cols):
                        cell_text = table_data[r][c]


                        cell_text = re.sub(r"\[(\d+)\]", r"[\1]", cell_text)

                        table.rows[r].cells[c].text = format_markdown(cell_text)

            continue

        
        elif line.startswith("### "):
            doc.add_heading(format_markdown(line.replace("### ", "")), level=3)

        elif line.startswith("#### "):
            doc.add_heading(format_markdown(line.replace("#### ", "")), level=4)

        
        else:
            if line.strip():
                doc.add_paragraph(format_markdown(line))

        i += 1



def generate_docx(topic: str, report: dict, filename="research_paper.docx"):
    doc = Document()

    # Title
    doc.add_heading(topic, 0)

    # Author
    doc.add_paragraph("AI Research Assistant")

    # Sections
    for i, (section, text) in enumerate(report.items(), start=1):
        doc.add_heading(f"{i}. {section}", level=2)

        process_text(doc, text)

    doc.save(filename)

    return filename