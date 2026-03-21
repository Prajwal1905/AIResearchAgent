from app.services.search import search_web
from app.services.scraper import scrape_url
from app.agents.summarizer import summarize_text
from app.services.pubmed import search_pubmed
from app.services.research_router import route_research

def research_topic(topic: str):
    result = route_research(topic)

    return result