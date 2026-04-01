from fastapi import FastAPI
from app.schemas.request import TopicRequest
from app.agents.writer import generate_critical_analysis
from app.agents.researcher import research_topic
from app.utils.pdf_generator import generate_pdf
from fastapi.responses import FileResponse
from app.agents.followup import answer_followup
from app.agents.perspective import generate_perspectives
from app.agents.comparator import compare_topics

from fastapi.middleware.cors import CORSMiddleware 
from app.utils.docx_generator import generate_docx
from pydantic import BaseModel
from app.agents.writer import write_full_report
import os

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
       
        if " vs " in data.topic.lower():
            comparison = compare_topics(data.topic)
            return {
                "topic": data.topic,
                "type": "comparison",
                "result": comparison
            }

        
        try:
            research_result = research_topic(data.topic)
        except Exception as e:
            print("RESEARCH ERROR:", e)
            research_result = {
                "domain": "General",
                "source": "Fallback",
                "data": []
            }

        full_report = write_full_report(data.topic, research_result)

        analysis = generate_critical_analysis(data.topic, research_result)
        perspectives = generate_perspectives(data.topic, research_result)
        
        refs=format_references(research_result.get("data",[]))
        return {
            "type": "research",
            "topic": data.topic,
            "domain": research_result.get("domain"),
            "source": research_result.get("source"),
            "sections":{
                "Full Report":full_report,
            },
            "perspectives": perspectives,
            "critical_analysis": analysis,
            "references": refs,
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

        
        if not os.path.exists(file_path):
            return {"error": "PDF not generated"}

        return FileResponse(
            path=file_path,
            filename="research_report.pdf",
            media_type="application/pdf"   
        )

    except Exception as e:
        print("PDF ERROR:", e)
        return {"error": str(e)}
    
@app.post("/download-docx")
def download_docx(data: dict):
    try:
        file_path = generate_docx(
            data.get("topic"),
            data.get("sections")
        )

        if not os.path.exists(file_path):
            return {"error": "DOCX not generated"}

        return FileResponse(
            path=file_path,
            filename="research_report.docx",
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    except Exception as e:
        print("DOCX ERROR:", e)
        return {"error": str(e)}