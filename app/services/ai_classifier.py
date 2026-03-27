import json
import re
from app.services.llm import generate_text


def classify_query(topic: str) -> dict:
    prompt = f"""
Classify the query into domain and best source.

Query: {topic}

Rules:
- medical → pubmed
- AI/ML → arxiv
- others → web

Return ONLY JSON:
{{
  "domain": "...",
  "source": "pubmed | arxiv | web"
}}
"""

    response = generate_text(prompt)

    
    try:
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
        else:
            result = {"domain": "general", "source": "web"}
    except Exception:
        result = {"domain": "general", "source": "web"}

    

    query_lower = topic.lower()

    if any(w in query_lower for w in ["health", "disease", "medical", "treatment"]):
        return {"domain": "medical", "source": "pubmed"}

    if any(w in query_lower for w in ["ai", "machine learning", "deep learning", "neural", "llm"]):
        return {"domain": "technology", "source": "arxiv"}

    
    return result