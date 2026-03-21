from app.services.domain_classifier import detect_domain
from app.services.pubmed import search_pubmed
from app.services.search import search_web


def route_research(topic: str):
    domain = detect_domain(topic)

    if domain == "healthcare":
        data = search_pubmed(topic)

    else:
        data = search_web(topic)

    return {
        "domain": domain,
        "data": data
    }