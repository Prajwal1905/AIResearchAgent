import requests
from bs4 import BeautifulSoup


def scrape_url(url: str) -> str:

    if not url or not url.startswith("http"):
        return ""

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=12)

        if response.status_code != 200:
            print(f"Scrape failed {url}: {response.status_code}")
            return ""

        soup = BeautifulSoup(response.text, "html.parser")

        
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        paragraphs = soup.find_all("p")

        # only keep paragraphs with real content
        clean = [p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50]

        text = " ".join(clean)
        return text[:4000]

    except Exception as e:
        print("Scrape error:", e)
        return ""
