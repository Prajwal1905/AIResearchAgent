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
from app.agents.fact_checker import fact_check_section
from fastapi.middleware.cors import CORSMiddleware 
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
            "date": item.get("date"),
            "url":item.get("url")
        })
    return refs

@app.get("/")
def home():
    return {"message": "AI Research Agent is running "}


@app.post("/generate-report")
async def generate_report(data: TopicRequest):
    try:
        # comparison mode
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
        previous_content = ""

        for section in sections:
            content = write_section(
                data.topic,
                section,
                research_result,
                previous_content
            )

            checked_content = fact_check_section(
                data.topic,
                section,
                content,
                research_result.get("data", [])
            )

            report[section] = checked_content

            
            previous_content += f"\n{section}:\n{checked_content}\n"

        analysis = generate_critical_analysis(data.topic, research_result)
        perspectives = generate_perspectives(data.topic, research_result)

        return {
            "type": "research",
            "topic": data.topic,
            "domain": research_result.get("domain"),
            "source": research_result.get("source"),
            "sections": report,
            "perspectives": perspectives,
            "critical_analysis": analysis,
            "references": format_references(research_result.get("data", [])),
        }

    except Exception as e:
        return {"error": str(e)}
    
@app.post("/ask-followup")
def ask_followup(data: FollowUpRequest):
    answer = answer_followup(data.question, data.report)

    return {
        "question": data.question,
        "answer": answer
    }

@app.post("/download-pdf")
def download_pdf(data: dict):
    try:
        file_path = generate_pdf(
            data.get("topic"),
            data.get("sections")   
        )
        return FileResponse(file_path, filename="report.pdf")
    except Exception as e:
        return {"error": str(e)}