from ddgs import DDGS
from app.services.credibility import get_credibility_score

def search_web(query: str, max_results: int = 5):
    results = []

    BAD_SITES = ["zhihu", "reddit", "quora", "pinterest"]
    seen_titles = set()

    with DDGS() as ddgs:
        search_results = ddgs.text(query, max_results=max_results)

        for r in search_results:
            title = r.get("title", "")
            link = r.get("href", "")

            
            if any(bad in link.lower() for bad in BAD_SITES):
                continue

            
            if title in seen_titles:
                continue

            seen_titles.add(title)
            credibility, reason = get_credibility_score(link)
            results.append({
                "title": title,
                "link": link,
                "source": r.get("source") or "web",
                "date": r.get("date") or "unknown",
                "credibility": credibility,
                "credibility_reason": reason


            })

            
            if len(results) >= 3:
                break

    return results