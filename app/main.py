from fastapi import FastAPI
from app.schemas.request import TopicRequest
from app.prompts.research_prompt import get_research_prompt
from app.services.llm import generate_text
from app.agents.planner import create_plan
from app.agents.writer import write_section,generate_critical_analysis
from app.agents.researcher import research_topic
from app.utils.pdf_generator import generate_pdf
from fastapi.responses import FileResponse
from app.agents.followup import answer_followup
from app.agents.perspective import generate_perspectives
from app.agents.comparator import compare_topics
from pydantic import BaseModel

app = FastAPI()

class FollowUpRequest(BaseModel):
    question: str
    report: dict


def format_references(data):
    refs = []
    for i, item in enumerate(data, start=1):
        refs.append({
            "id": i,
            "title": item.get("title"),
            "source": item.get("source"),
            "date": item.get("date")
        })
    return refs

@app.get("/")
def home():
    return {"message": "AI Research Agent is running "}


@app.post("/generate-report")
def generate_report(data: TopicRequest):
    # detect comparison query
    if " vs " in data.topic.lower():
        comparison = compare_topics(data.topic)
        return {
           "topic": data.topic,
           "type": "comparison",
           "result": comparison
        }
    sections = create_plan(data.topic)
    research_result = research_topic(data.topic)

    report = {}

    for section in sections:
        content = write_section(data.topic, section, research_result)
        report[section] = content

    analysis = generate_critical_analysis(data.topic, research_result)
    perspectives = generate_perspectives(data.topic, research_result)
    return {
        "topic": data.topic,
        "domain": research_result["domain"],
        "source": research_result["source"],
        "sections": report,
        "perspectives": perspectives,
        "critical_analysis": analysis,
        "references": format_references(research_result["data"])
    }

@app.post("/ask-followup")
def ask_followup(data: FollowUpRequest):
    answer = answer_followup(data.question, data.report)

    return {
        "question": data.question,
        "answer": answer
    }