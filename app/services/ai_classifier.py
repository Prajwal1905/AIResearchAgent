from app.services.llm import generate_text


def classify_query(topic: str) -> dict:
    prompt = f"""
Classify the following query and decide the best data source.

Query: {topic}

Return ONLY JSON in this format:
{{
  "domain": "scientific / technical / general",
  "source": "pubmed / arxiv / web"
}}
"""

    response = generate_text(prompt)

    try:
        result = eval(response)
    except:
        result = {"domain": "general", "source": "web"}

    return result