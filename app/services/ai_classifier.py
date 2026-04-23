import json
import re
from app.services.llm import generate_text


def classify_query(topic: str) -> dict:

    query_lower = topic.lower()

    if any(w in query_lower for w in ["health", "disease", "medical", "treatment", "clinical", "drug", "patient", "hospital"]):
        return {"domain": "medical", "source": "pubmed"}

    if any(w in query_lower for w in ["ai", "machine learning", "deep learning", "neural", "llm", "transformer", "algorithm"]):
        return {"domain": "technology", "source": "arxiv"}

    if any(w in query_lower for w in ["law", "legal", "court", "regulation", "policy", "statute"]):
        return {"domain": "law", "source": "web"}

    if any(w in query_lower for w in ["finance", "stock", "economy", "market", "investment", "gdp", "inflation"]):
        return {"domain": "finance", "source": "web"}

    if any(w in query_lower for w in ["history", "war", "empire", "revolution", "ancient", "century"]):
        return {"domain": "history", "source": "web"}

    if any(w in query_lower for w in ["psychology", "mental health", "behavior", "cognitive", "therapy"]):
        return {"domain": "psychology", "source": "web"}

    
    prompt = f"""
Classify the query into domain and best source.

Query: {topic}

Rules:
- medical → pubmed
- AI/ML/technology → arxiv
- anything else → web

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
            return json.loads(json_match.group())
        else:
            return {"domain": "general", "source": "web"}
    except Exception:
        return {"domain": "general", "source": "web"}
