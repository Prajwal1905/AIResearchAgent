from app.services.llm import generate_text, describe_image
from app.services.file_reader import extract_text, extract_images_from_pdf, is_supported
import re


def start_file_chat(file_path: str, filename: str) -> dict:
    
    if not is_supported(filename):
        return {"error": "Unsupported file type. Supported: PDF, DOCX, TXT, PPTX, XLSX, CSV, EPUB"}

    text = extract_text(file_path)

    if not text or len(text) < 100:
        return {"error": "Could not extract text from this file."}

    content = text[:8000]

    # extract images only from PDFs
    images = []
    if filename.lower().endswith(".pdf"):
        images = extract_images_from_pdf(file_path, max_images=5)
        print(f"Found {len(images)} images in PDF")

    print(f"Generating summary for: {filename}")

    summary_prompt = f"""
Read this document and provide:
1. File type and document title (if visible)
2. Type of document (research paper, report, spreadsheet, presentation, etc.)
3. Main topic in one sentence
4. Key sections or chapters (list up to 6)
5. Approximate size
6. Number of figures/diagrams: {len(images)}

Document:
{content[:2000]}

Keep it brief and clear.
"""
    summary = generate_text(summary_prompt)

    return {
        "content": content,
        "summary": summary,
        "images": images,
        "image_count": len(images),
        "char_count": len(content),
        "word_count": len(content.split())
    }


def chat_with_file(question: str, content: str, history: list = None, images: list = None) -> str:
    

    question_lower = question.lower()

    # detect if user is asking about an image
    is_image_question = any(word in question_lower for word in [
        "figure", "diagram", "chart", "image", "picture", "graph",
        "illustration", "fig", "show", "look like", "visual", "draw",
        "explain the", "what is shown", "describe the"
    ])

    if is_image_question and images:
        return _answer_with_images(question, content, images, history)

    return _answer_text(question, content, history)


def _answer_text(question: str, content: str, history: list = None) -> str:
    
    history_text = ""
    if history:
        recent = history[-5:]
        for item in recent:
            history_text += f"Q: {item['question']}\nA: {item['answer']}\n\n"

    prompt = f"""
You are an expert document analyst.

Document content:
{content}

Previous conversation:
{history_text}

User question: {question}

Instructions:
- Answer ONLY based on the document content above
- If the answer is not in the document, say "This information is not in the document"
- Quote specific parts when relevant
- Be clear and direct — no hedging or guessing

Answer:
"""

    system_prompt = "You are an expert document analyst who answers questions accurately based only on the provided document content."
    return generate_text(prompt, system_prompt=system_prompt)


def _answer_with_images(question: str, content: str, images: list, history: list = None) -> str:
    

    question_lower = question.lower()

    # find specific figure number if mentioned
    target_images = images
    fig_match = re.search(r"fig(?:ure)?\s*\.?\s*(\d+)", question_lower)
    if fig_match:
        fig_num = int(fig_match.group(1))
        specific = [img for img in images if img["index"] == fig_num]
        if specific:
            target_images = specific
            print(f"User asked about figure {fig_num} specifically")

    # describe each relevant image using vision
    descriptions = []
    for img in target_images[:3]:
        print(f"Analyzing image {img['index']} on page {img['page']} with high detail")
        description = describe_image(
            base64_image=img["base64"],
            image_ext=img["ext"],
            caption=img.get("caption", ""),
            context=content[:500]
        )
        descriptions.append({
            "figure_num": img["index"],
            "page": img["page"],
            "caption": img.get("caption", ""),
            "description": description
        })

    if not descriptions:
        return _answer_text(question, content, history)

    # build image context
    image_context = "\n\n".join([
        f"Figure {d['figure_num']} (Page {d['page']}):\nCaption: {d['caption']}\nWhat is visible: {d['description']}"
        for d in descriptions
    ])

    # now answer the user question using image descriptions
    prompt = f"""
You are an expert document analyst answering a question about figures in a document.

What is actually visible in the figures (from direct image analysis):
{image_context}

Additional document text context:
{content[:1500]}

User question: {question}

Instructions:
- Use the image analysis above as your PRIMARY source
- Be specific about what labels, text, objects, arrows are visible
- Do NOT say "likely" or "probably" — only state what was actually seen
- If multiple panels or examples are shown, describe each one
- Be direct and precise

Answer:
"""

    return generate_text(prompt)

def start_pdf_chat(file_path: str) -> dict:
    return start_file_chat(file_path, "document.pdf")


def chat_with_pdf(question: str, content: str, history: list = None) -> str:
    return chat_with_file(question, content, history)
