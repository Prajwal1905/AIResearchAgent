from app.services.ai_classifier import classify_query
from app.services.pubmed import search_pubmed
from app.services.search import search_web
from app.services.arxiv import search_arxiv

def route_research(topic: str):
    decision = classify_query(topic)

    source = decision["source"]
    domain = decision["domain"]

    web_data = search_web(f"{topic} research report analysis data")

    if source == "pubmed":
        pubmed_data = search_pubmed(topic)
        data = pubmed_data + web_data

    elif source == "arxiv":
        arxiv_data = search_arxiv(topic)
        data = arxiv_data + web_data

    else:
        data = web_data

    return {
        "domain": domain,
        "source": source,
        "data": data
    }