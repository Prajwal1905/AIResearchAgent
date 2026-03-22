from app.services.llm import generate_text


def compare_topics(topic: str):
    prompt = f"""
You are an expert analyst.

The user wants to compare topics.

Topic: {topic}

Instructions:
- Identify the two (or more) entities to compare
- Compare them in structured format:

Comparison:

1. Use Cases
2. Advantages
3. Risks
4. ROI / Impact
5. When to choose what

Be clear, structured, and analytical.
"""

    return generate_text(prompt)