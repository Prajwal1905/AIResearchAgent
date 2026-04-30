import requests
from app.core.config import TAVILY_API_KEY


def search_web(query: str, max_results: int = 5):

    if not query:
        return []

    try:
        response = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": TAVILY_API_KEY,
                "query": query,
                "max_results": max_results,
                "search_depth": "advanced",  
                "include_answer": False,
            },
            timeout=15
        )

        if response.status_code != 200:
            print("Tavily search failed:", response.status_code)
            return []

        data = response.json()
        raw_results = data.get("results", [])

        if not raw_results:
            print("Tavily returned no results for:", query)
            return []

        results = []
        for item in raw_results:
            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "source": "web",
                "date": item.get("published_date", ""),
                "snippet": item.get("content", "")  
            })

        print(f"Tavily returned {len(results)} results for: {query}")
        return results

    except Exception as e:
        print("Search error:", e)
        return []
