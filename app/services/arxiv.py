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
    root = ET.fromstring(response.content)

    papers = []

    namespace = {"atom": "http://www.w3.org/2005/Atom"}

    entries = root.findall("atom:entry", namespace)

    for i, entry in enumerate(entries):
        title = entry.find("atom:title", namespace).text.strip()
        link = entry.find("atom:id", namespace).text.strip()
        published = entry.find("atom:published", namespace).text[:10]

        papers.append({
            
            "title": title,
            "url": link,
            "date": published,
            "source": "arxiv"
        })

    return papers