from app.services.llm import generate_text
from app.services.file_reader import extract_text, is_supported


def start_file_chat(file_path: str, filename: str) -> dict:
    
    if not is_supported(filename):
        return {"error": f"Unsupported file type. Supported: PDF, DOCX, TXT, PPTX, XLSX, CSV, EPUB"}

    text = extract_text(file_path)

    if not text or len(text) < 100:
        return {"error": "Could not extract text from this file. Make sure it is not a scanned image or empty file."}

    
    content = text[:8000]

    print(f"Generating summary for: {filename}")

    summary_prompt = f"""
Read this document and provide:
1. File type and document title (if visible)
2. Type of document (research paper, report, spreadsheet, presentation, etc.)
3. Main topic in one sentence
4. Key sections or chapters (list up to 6)
5. Approximate size (number of pages or rows)

Document:
{content[:2000]}

Keep it brief and clear.
"""
    summary = generate_text(summary_prompt)

    return {
        "content": content,
        "summary": summary,
        "char_count": len(content),
        "word_count": len(content.split())
    }


def chat_with_file(question: str, content: str, history: list = None) -> str:
    

    history_text = ""
    if history:
        recent = history[-5:]
        for item in recent:
            history_text += f"Q: {item['question']}\nA: {item['answer']}\n\n"

    prompt = f"""
You are an expert document analyst. You have been given a document to analyze.

Document content:
{content}

Previous conversation:
{history_text}

User question: {question}

Instructions:
- Answer ONLY based on the document content above
- If the answer is not in the document, say "This information is not in the document"
- Quote specific parts when relevant
- Be clear and concise
- If asked to summarize a section, find that section and summarize it
- If the document is a spreadsheet or CSV, analyze the data patterns
- If the document is a presentation, refer to specific slides

Answer:
"""

    system_prompt = "You are an expert document analyst who answers questions accurately based only on the provided document content."
    return generate_text(prompt, system_prompt=system_prompt)


def start_pdf_chat(file_path: str) -> dict:
    return start_file_chat(file_path, "document.pdf")


def chat_with_pdf(question: str, content: str, history: list = None) -> str:
    return chat_with_file(question, content, history)
