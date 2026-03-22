def get_credibility_score(link: str):
    link = link.lower()

    # HIGH credibility
    if any(x in link for x in [".gov", ".edu", "nih", "who", "pubmed"]):
        return "High", "Trusted Source"

    # MEDIUM credibility
    elif any(x in link for x in ["news", "bbc", "forbes", "reuters"]):
        return "Medium", "News / Media"

    # LOW credibility
    else:
        return "Low", "General Web"