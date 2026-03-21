from ddgs import DDGS


def search_web(query: str, max_results: int = 5):
    results = []

    with DDGS() as ddgs:
        search_results = ddgs.text(query, max_results=max_results)

        for r in search_results:
            results.append({
                "title": r.get("title"),
                "link": r.get("href")
            })

    return results