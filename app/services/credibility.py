def get_credibility_score(link: str):
    link = link.lower()

    score = 50   # base score
    category = "General Web"

    #  HIGH TRUST SOURCES
    if any(x in link for x in [".gov", ".edu"]):
        score += 40
        category = "Government / Academic"

    if any(x in link for x in ["nih", "who", "pubmed", "arxiv", "ieee", "springer"]):
        score += 35
        category = "Scientific / Research"

    # NEWS SOURCES
    if any(x in link for x in ["bbc", "reuters", "nytimes", "forbes", "bloomberg"]):
        score += 20
        category = "Reputed News"

    #  MEDIUM SOURCES
    if any(x in link for x in ["medium.com", "towardsdatascience", "analyticsvidhya"]):
        score += 10
        category = "Tech Blog"

    #  LOW TRUST / PENALTY
    if any(x in link for x in ["blogspot", "wordpress", "randomsite"]):
        score -= 20
        category = "Unverified Blog"

    #  VERY LOW / SPAM
    if any(x in link for x in ["clickbait", "ads", "sponsored"]):
        score -= 30
        category = "Low Credibility"

    #  Clamp score
    score = max(0, min(score, 100))

    #  Label
    if score >= 80:
        label = "High"
    elif score >= 60:
        label = "Medium"
    else:
        label = "Low"

    return {
        "score": score,
        "label": label,
        "category": category
    }