from app.services.ai_classifier import classify_query
from app.services.pubmed import search_pubmed
from app.services.search import search_web
from app.services.arxiv import search_arxiv


def route_research(topic: str):

    decision = classify_query(topic)

    source = decision["source"]
    domain = decision["domain"]

   
    if source == "pubmed":
        data = search_pubmed(topic)

    elif source == "arxiv":
        data = search_arxiv(topic)

    else:
        data = search_web(f"{topic} research report analysis")

   
    if len(data) < 3:
        extra = search_web(f"{topic} research report analysis")
        data = data + extra

    return {
        "domain": domain,
        "source": source,
        "data": data
    }
