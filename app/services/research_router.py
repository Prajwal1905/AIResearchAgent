from app.services.ai_classifier import classify_query
from app.services.pubmed import search_pubmed
from app.services.search import search_web


def route_research(topic: str):
    decision = classify_query(topic)

    source = decision["source"]

    if source == "pubmed":
        data = search_pubmed(topic)

    else:
        data = search_web(f"{topic} research report analysis data")

    return {
        "domain": decision["domain"],
        "source": source,
        "data": data
    }