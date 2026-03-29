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

    
        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.text, "html.parser")

        links = soup.select(".result__a")

        for link in links[:max_results]:
            try:
                title = link.get_text(strip=True)
                href = link.get("href")

                if not href or not title:
                    continue

                
                try:
                    cred = get_credibility_score(href)

                    if isinstance(cred, dict):
                        score = cred.get("score", 0)
                    else:
                        score = cred
                except Exception:
                    score = 0

                
                results.append({
                    "title": title,
                    "url": href,
                    "source": "web",
                    "date": "",
                    "credibility": score
                })

            except Exception as inner:
                print("INNER LINK ERROR:", inner)
                continue

    except Exception as e:
        print("SEARCH ERROR:", e)
        return []

    return results