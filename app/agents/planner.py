from app.services.llm import generate_text


def create_plan(topic: str):
    prompt = f"""
You are a research planner.

Break the following topic into 5 to 7 well-structured sections.

Topic: {topic}

Return ONLY a Python list.
Example:
["Introduction", "Applications", "Challenges", "Conclusion"]
"""

    response = generate_text(prompt)

    try:
        sections = eval(response)  # simple parsing (we improve later)
    except:
        sections = ["Introduction", "Main Content", "Conclusion"]

    return sections