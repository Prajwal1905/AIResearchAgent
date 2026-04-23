import json
from app.services.llm import generate_text


def create_plan(topic: str, custom_format: str = None):

   
    if custom_format:
        prompt = f"""
You are an academic research planner.

A user has provided a custom research paper format.

Topic: {topic}

Format:
{custom_format}

Extract the section headings from this format and return them as a JSON list.

Return ONLY a valid JSON list. No explanation.
"""
    else:
        prompt = f"""
You are an academic research planner.

Generate a structured research paper outline for this topic.

Topic: {topic}

Use standard academic structure:
- Abstract
- Introduction
- Literature Review
- Methodology
- Findings
- Discussion
- Conclusion
- Future Work

Return ONLY a JSON list. No explanation.
"""

    response = generate_text(prompt)

    try:
        
        clean = response.strip().replace("```json", "").replace("```", "").strip()
        sections = json.loads(clean)
    except Exception as e:
        print("Planner JSON parse failed:", e)
        sections = [
            "Abstract",
            "Introduction",
            "Literature Review",
            "Methodology",
            "Findings",
            "Discussion",
            "Conclusion",
            "Future Work"
        ]

    return sections
