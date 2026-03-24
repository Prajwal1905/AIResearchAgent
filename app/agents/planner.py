from app.services.llm import generate_text
import json


def create_plan(topic: str, custom_format: str = None):
    if custom_format:
        prompt = f"""
You are an academic research planner.

A user has provided a custom research paper format.

Topic: {topic}

Format:
{custom_format}

Extract the section headings from this format and return them as a Python list.

Return ONLY a valid JSON list.
"""
    else:
        prompt = f"""
You are an academic research planner.

Generate a structured research paper outline for the topic below.

Topic: {topic}

Follow STANDARD academic structure:

- Abstract
- Introduction
- Literature Review
- Methodology
- Findings / Results
- Discussion
- Conclusion
- Future Work

Rules:
- Return ONLY a JSON list
- No explanation
- No repetition
"""

    response = generate_text(prompt)

    try:
        sections = json.loads(response)
    except:
        sections = [
            "Abstract",
            "Introduction",
            "Literature Review",
            "Methodology",
            "Findings",
            "Discussion",
            "Conclusion",
            "Future Work",
        ]

    return sections