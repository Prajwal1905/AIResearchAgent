import fitz  
import os


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract clean text from a PDF file.
    Returns extracted text as a string.
    """
    if not os.path.exists(file_path):
        print(f"PDF not found: {file_path}")
        return ""

    try:
        doc = fitz.open(file_path)
        full_text = ""

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            full_text += text + "\n"

        doc.close()

        # clean up excessive whitespace
        lines = [line.strip() for line in full_text.split("\n") if line.strip()]
        clean_text = "\n".join(lines)

        print(f"Extracted {len(clean_text)} chars from {os.path.basename(file_path)}")
        return clean_text

    except Exception as e:
        print(f"PDF extraction error: {e}")
        return ""


def extract_text_from_multiple_pdfs(file_paths: list) -> list:
    """
    Extract text from multiple PDFs.
    Returns list of dicts with filename and text.
    """
    results = []

    for path in file_paths:
        text = extract_text_from_pdf(path)
        if text:
            results.append({
                "filename": os.path.basename(path),
                "text": text[:5000],  
                "path": path
            })

    return results
