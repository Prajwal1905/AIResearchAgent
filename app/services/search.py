import requests
from bs4 import BeautifulSoup
from app.services.credibility import get_credibility_score


def search_web(query: str, max_results: int = 3):
    results = []

    try:
        url = f"https://duckduckgo.com/html/?q={query}"
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        links = soup.select(".result__a")

        for link in links[:max_results]:
            try:
                title = link.get_text()
                href = link.get("href")

                if not href:
                    continue

                
                cred = get_credibility_score(href)

                credibility = cred.get("label")
                reason = cred.get("category")
                score = cred.get("score")

                results.append({
                    "title": title,
                    "url": href,
                    "source": "web",
                    "date": "unknown",
                    "credibility": credibility,
                    "credibility_reason": reason,
                    "credibility_score": score
                })

            except Exception as inner:
                print("INNER LINK ERROR:", inner)

    except Exception as e:
        print("SEARCH ERROR:", e)

    return results