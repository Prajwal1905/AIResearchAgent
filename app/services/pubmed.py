import requests


def format_query(query):
    keywords = [w for w in query.split() if len(w) > 3]
    if not keywords:
        return "health"
    return " OR ".join(keywords[:5]) + " AND (review OR study)"


def search_pubmed(query: str, max_results: int = 3):
    
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

    params = {
        "db": "pubmed",
        "term": format_query(query),
        "retmode": "json",
        "retmax": max_results
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        return []

    try:
        data = response.json()
    except Exception:
        print("PubMed JSON parse error")
        return []

    ids = data.get("esearchresult", {}).get("idlist", [])

    if not ids:
        return []

    
    fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

    fetch_params = {
        "db": "pubmed",
        "id": ",".join(ids),
        "retmode": "json"
    }

    fetch_response = requests.get(fetch_url, params=fetch_params)

    if fetch_response.status_code != 200:
        return []

    try:
        fetch_data = fetch_response.json()
    except Exception:
        print("PubMed fetch JSON error")
        return []

    result = fetch_data.get("result", {})

    papers = []

    for pid in ids:
        paper = result.get(pid)
        if not paper:
            continue

        papers.append({
            "title": paper.get("title"),
            "date": paper.get("pubdate"),
            "source": paper.get("source"),
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pid}/"
        })

    return papers