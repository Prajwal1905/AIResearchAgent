from app.services.search import search_web
from app.services.scraper import scrape_url
from app.agents.summarizer import summarize_text
from app.services.research_router import route_research
from app.services.credibility import get_credibility_score
from concurrent.futures import ThreadPoolExecutor


def research_topic(topic: str):
    
    routed_result = route_research(topic)

    raw_data = routed_result.get("data", [])
    domain = routed_result.get("domain", "general")
    source = routed_result.get("source", "mixed")


    
    def process_item(item):
        url = item.get("url") or "https://www.google.com"

        try:
            content = scrape_url(url)

            if not content or len(content) < 200:
                return None

            summary = summarize_text(content)

            credibility_data = get_credibility_score(url)

            
            if isinstance(credibility_data, dict):
                credibility_score = credibility_data.get("score", 0)
            else:
                credibility_score = credibility_data

            return {
                "title": item.get("title"),
                "url": url,
                "summary": summary,
                "credibility": credibility_score,
                "source": item.get("source"),
                "date": item.get("date")
            }

        except Exception:
            return None


    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(process_item, raw_data))

    # remove failed ones
    enriched_data = [r for r in results if r]


   
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