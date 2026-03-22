from app.services.llm import generate_text


def generate_perspectives(topic: str, research_result: dict):
    data = research_result["data"]

    context = "\n".join([str(item) for item in data])

    prompt = f"""
You are an expert analyst.

Topic: {topic}

Based on the research data:
{context}

Generate analysis from different perspectives:

1. Economic Perspective
2. Startup Founder Perspective
3. Investor Perspective

For each:
- Give insights
- Mention implications
- Be clear and analytical

Do not repeat same points.
"""

    return generate_text(prompt)