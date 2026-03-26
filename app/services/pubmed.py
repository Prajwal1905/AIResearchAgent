import requests

def format_query(query):
    # keep only important keywords
    keywords = [w for w in query.split() if len(w) > 3]

    if not keywords:
        return "health"

    # 🔥 force PubMed-friendly query
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
    data = response.json()

    ids = data.get("esearchresult", {}).get("idlist", [])
    if not ids:
        print("Retrying with simplified query...")

    
        simple_query = "artificial intelligence healthcare"

        params["term"] = simple_query
        response = requests.get(url, params=params)
        data = response.json()

        ids = data.get("esearchresult", {}).get("idlist", [])

        if not ids:
           print("No PubMed results found")
           return []
    papers = []

    fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

    fetch_params = {
        "db": "pubmed",
        "id": ",".join(ids),
        "retmode": "json"
    }

    fetch_response = requests.get(fetch_url, params=fetch_params)
    fetch_data = fetch_response.json()

    result = fetch_data.get("result", {})

    for pid in ids:
        paper = result.get(pid)

        if not paper:
            continue  

        papers.append({
            "id":len(papers)+1,
            "title": paper.get("title"),
            "date": paper.get("pubdate"),
            "source": paper.get("source"),
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pid}/"
        })

    return papers