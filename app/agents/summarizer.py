from app.services.llm import generate_text


def summarize_text(text: str) -> str:
    prompt = f"""
Summarize the following content into key points:

{text}

Make it:
- Short
- Informative
- Bullet points
"""

    return generate_text(prompt)