import requests
from app.core.config import BRAVE_API_KEY


def search_web(query: str, max_results: int = 5):

    if not query:
        return []

    url = "https://api.search.brave.com/res/v1/web/search"

    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": BRAVE_API_KEY
    }

    params = {
        "q": query,
        "count": max_results
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)

        if response.status_code != 200:
            print("Brave Search error:", response.status_code)
            return []

        data = response.json()
        raw_results = data.get("web", {}).get("results", [])

        results = []
        for item in raw_results:
            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "source": "web",
                "date": item.get("page_age", ""),
                "snippet": item.get("description", "")
            })

        return results

    except Exception as e:
        print("Search error:", e)
        return []
