from app.services.llm import generate_text


def write_section(topic: str, section: str, research_result: dict) -> str:
    domain = research_result["domain"]
    data = research_result["data"]

    context = "\n".join([
        str(item) for item in data
    ])

    prompt = f"""
You are an expert research writer.

Domain: {domain}
Topic: {topic}
Section: {section}

Use this research data:
{context}

Write a detailed, accurate, and professional section.
Adapt writing style based on domain.
"""

    return generate_text(prompt)