import requests
import xml.etree.ElementTree as ET


def search_arxiv(query: str, max_results: int = 3):
    url = "http://export.arxiv.org/api/query"

    params = {
        "search_query": query,
        "start": 0,
        "max_results": max_results
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        return []

    try:
        root = ET.fromstring(response.content)
    except Exception:
        print("arXiv XML parse error")
        return []

    namespace = {"atom": "http://www.w3.org/2005/Atom"}
    entries = root.findall("atom:entry", namespace)

    papers = []

    for entry in entries:
        try:
            title = entry.find("atom:title", namespace).text.strip()
            link = entry.find("atom:id", namespace).text.strip()
            published = entry.find("atom:published", namespace).text[:10]

            papers.append({
                "title": title,
                "url": link,
                "date": published,
                "source": "arxiv"
            })

        except Exception:
            continue

    return papers