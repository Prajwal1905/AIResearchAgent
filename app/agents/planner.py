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

Extract the section headings from this format and return them as a JSON list of strings.

Return ONLY a valid flat JSON list of strings. No nested lists. No explanation.

Example: ["Abstract", "Introduction", "Methodology", "Conclusion"]
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

Return ONLY a flat JSON list of strings. No nested lists. No explanation.

Example: ["Abstract", "Introduction", "Methodology", "Conclusion"]
"""

    response = generate_text(prompt)

    try:
        clean = response.strip().replace("```json", "").replace("```", "").strip()
        sections = json.loads(clean)

        
        flat = []
        for item in sections:
            if isinstance(item, list):
                flat.extend([str(i) for i in item])
            else:
                flat.append(str(item))
        sections = flat

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
