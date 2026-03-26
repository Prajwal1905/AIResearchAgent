import requests


def search_pubmed(query: str, max_results: int = 3):
    
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": max_results
    }

    response = requests.get(url, params=params)
    data = response.json()

    ids = data["esearchresult"]["idlist"]

    papers = []

    
    fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

    fetch_params = {
        "db": "pubmed",
        "id": ",".join(ids),
        "retmode": "json"
    }

    fetch_response = requests.get(fetch_url, params=fetch_params)
    fetch_data = fetch_response.json()

    for pid in ids:
        paper = fetch_data["result"][pid]

        papers.append({
            "title": paper.get("title"),
            "date": paper.get("pubdate"),
            "source": paper.get("source"),
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pid}/"
        })

    return papers