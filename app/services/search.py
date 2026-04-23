import requests
import logging
from urllib.parse import urlencode
from app.core.config import BRAVE_API_KEY

logger = logging.getLogger(__name__)

BRAVE_SEARCH_URL = "https://api.search.brave.com/res/v1/web/search"

HEADERS = {
    "Accept": "application/json",
    "Accept-Encoding": "gzip",
    "X-Subscription-Token": BRAVE_API_KEY,
}


def search_web(query: str, max_results: int = 5) -> list:
    
    if not query or not query.strip():
        logger.warning("search_web called with empty query")
        return []

    if not BRAVE_API_KEY:
        logger.error("BRAVE_API_KEY not set in environment")
        return []

    params = {
        "q": query,
        "count": max_results,
        "search_lang": "en",
        "safesearch": "moderate",
        "freshness": "py",      
        "text_decorations": False,
        "spellcheck": True,
    }

    try:
        response = requests.get(
            BRAVE_SEARCH_URL,
            headers=HEADERS,
            params=params,
            timeout=10,
        )

        if response.status_code == 401:
            logger.error("Brave Search API: Invalid API key")
            return []

        if response.status_code == 429:
            logger.warning("Brave Search API: Rate limit hit")
            return []

        if response.status_code != 200:
            logger.warning(f"Brave Search API: Unexpected status {response.status_code}")
            return []

        data = response.json()
        raw_results = data.get("web", {}).get("results", [])

        if not raw_results:
            logger.info(f"Brave Search returned 0 results for: {query}")
            return []

        results = []
        for item in raw_results[:max_results]:
            url = item.get("url", "")
            if not url:
                continue

            results.append({
                "title": item.get("title", "Untitled"),
                "url": url,
                "source": "web",
                "date": item.get("page_age", ""),       
                "snippet": item.get("description", ""), 
            })

        logger.info(f"Brave Search returned {len(results)} results for: {query}")
        return results

    except requests.Timeout:
        logger.warning(f"Brave Search timed out for query: {query}")
        return []

    except requests.ConnectionError:
        logger.error("Brave Search: Connection error — check internet/API endpoint")
        return []

    except Exception as e:
        logger.error(f"Brave Search unexpected error: {e}")
        return []
