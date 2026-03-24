from app.services.llm import generate_text


def fact_check_section(topic: str, section: str, content: str, research_data: list):
    context = "\n".join([item.get("summary", "") for item in research_data])

    prompt = f"""
You are a strict academic fact-checker.

Topic: {topic}
Section: {section}

Content to verify:
{content}

Reference data:
{context}

Tasks:
1. Identify any incorrect or unsupported claims
2. Correct them using the reference data
3. Strengthen weak arguments
4. Ensure all claims are logically valid

Rules:
- Do NOT rewrite completely
- Only improve factual accuracy
- Keep original structure
- Be precise and critical
"""

    return generate_text(prompt)