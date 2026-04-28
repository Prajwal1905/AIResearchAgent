from app.services.llm import generate_text
from app.services.pdf_reader import extract_text_from_pdf


def start_pdf_chat(file_path: str) -> dict:
    

    text = extract_text_from_pdf(file_path)

    if not text or len(text) < 100:
        return {"error": "Could not extract text from PDF. Make sure it is not a scanned image."}

    
    content = text[:8000]

    print("Generating document summary...")

    
    summary_prompt = f"""
Read this document and provide:
1. Title (if visible)
2. Type of document (research paper, report, textbook, article, etc.)
3. Main topic in one sentence
4. Key sections or chapters (list up to 6)
5. Total estimated pages worth of content

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


def chat_with_pdf(question: str, content: str, history: list = None) -> str:
    
    #  conversation history context
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
- Quote specific parts of the document when relevant
- Be clear and concise
- If asked to summarize a section, find that section and summarize it
- If asked to compare or explain, do so analytically

Answer:
"""

    system_prompt = "You are an expert document analyst who answers questions accurately based only on the provided document content."
    return generate_text(prompt, system_prompt=system_prompt)
