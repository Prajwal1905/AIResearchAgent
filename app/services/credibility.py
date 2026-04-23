from urllib.parse import unquote


def get_credibility_score(link: str):

    if not link:
        return {"score": 0, "label": "Low", "category": "Unknown"}

    # decode encoded URLs like DDG redirects
    link = unquote(link).lower()

    score = 50
    category = "General Web"

    # government and university sites
    if any(x in link for x in [".gov", ".edu", ".ac.uk"]):
        score += 40
        category = "Government / Academic"

    # research and science databases
    if any(x in link for x in ["pubmed", "arxiv", "nih", "who", "ieee", "springer", "nature.com", "sciencedirect", "jstor", "ncbi"]):
        score += 35
        category = "Scientific / Research"

    # trusted news sources
    if any(x in link for x in ["bbc", "reuters", "nytimes", "bloomberg", "forbes", "theguardian", "apnews"]):
        score += 20
        category = "Reputed News"

    # tech blogs and publications
    if any(x in link for x in ["towardsdatascience", "analyticsvidhya", "wired", "techcrunch"]):
        score += 10
        category = "Tech Blog"

    # low trust sources
    if any(x in link for x in ["blogspot", "wordpress.com", "tumblr"]):
        score -= 15
        category = "Unverified Blog"

    
    if any(x in link for x in ["clickbait", "sponsored", "ads."]):
        score -= 30
        category = "Low Credibility"

    score = max(0, min(score, 100))

    if score >= 80:
        label = "High"
    elif score >= 55:
        label = "Medium"
    else:
        label = "Low"

    return {
        "score": score,
        "label": label,
        "category": category
    }
