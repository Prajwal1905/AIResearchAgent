from fastapi import FastAPI
from app.schemas.request import TopicRequest
from app.prompts.research_prompt import get_research_prompt
from app.services.llm import generate_text
from app.agents.planner import create_plan
from app.agents.writer import write_section
from app.agents.researcher import research_topic
from app.utils.pdf_generator import generate_pdf
from fastapi.responses import FileResponse

app = FastAPI()


@app.get("/")
def home():
    return {"message": "AI Research Agent is running "}


@app.post("/generate-report")
def generate_report(data: TopicRequest):
    sections = create_plan(data.topic)
    research_result = research_topic(data.topic)

    report = {}

    for section in sections:
        content = write_section(data.topic, section, research_result)
        report[section] = content

    return {
        "topic": data.topic,
        "domain": research_result["domain"],
        "sections": report,
        "sources": research_result["data"]
    }