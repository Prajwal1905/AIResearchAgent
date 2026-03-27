from app.services.search import search_web
from app.services.scraper import scrape_url
from app.agents.summarizer import summarize_text
from app.services.research_router import route_research
from app.services.credibility import get_credibility_score


def research_topic(topic: str):
    
    routed_result = route_research(topic)

    raw_data = routed_result.get("data", [])
    domain = routed_result.get("domain", "general")
    source = routed_result.get("source", "mixed")

    enriched_data = []

    for item in raw_data:
        url = item.get("url")
        if not url:
            url = "https://www.google.com"

        try:
            content = scrape_url(url)

            if not content or len(content) < 200:
                continue

            summary = summarize_text(content)
            credibility_data = get_credibility_score(url)
            if isinstance(credibility_data, dict):
                credibility_score = credibility_data.get("score", 0)
            else:
                credibility_score = credibility_data
            enriched_data.append({
                "title": item.get("title"),
                "url": url,
                "summary": summary,
                "credibility": credibility_score,
                "source": item.get("source"),
                "date": item.get("date")
            })

        except Exception:
            continue

    
    enriched_data = sorted(
        enriched_data,
        key=lambda x: x.get("credibility", 0),
        reverse=True
    )

    top_data = enriched_data[:5]

    
    references = []
    for item in top_data:
        references.append({
            "id": len(references) + 1,
            "title": item.get("title"),
            "url": item.get("url"),
            "source": item.get("source")
        })

    
    return {
        "domain": domain,
        "source": source,
        "data": top_data,
        "references": references   
    }