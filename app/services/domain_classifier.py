def detect_domain(topic: str) -> str:
    topic = topic.lower()

    if any(word in topic for word in ["health", "medical", "disease", "cancer", "treatment"]):
        return "healthcare"

    elif any(word in topic for word in ["ai", "machine learning", "deep learning", "neural network"]):
        return "tech"

    else:
        return "general"