from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os

from app.schemas.request import TopicRequest
from app.agents.writer import write_full_report, generate_critical_analysis
from app.agents.researcher import research_topic
from app.agents.followup import answer_followup
from app.agents.perspective import generate_perspectives
from app.agents.comparator import compare_topics
from app.agents.planner import create_plan
from app.utils.pdf_generator import generate_pdf
from app.utils.docx_generator import generate_docx


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class FollowUpRequest(BaseModel):
    question: str
    report: dict

class DownloadRequest(BaseModel):
    topic: str
    sections: dict


@app.get("/")
def home():
    return {"message": "AI Research Agent is running"}


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

        #  research the topic
        try:
            research_result = research_topic(data.topic)
        except Exception as e:
            print("Research error:", e)
            research_result = {
                "domain": "General",
                "source": "Fallback",
                "data": [],
                "references": []
            }

        #  create section plan
        plan = create_plan(data.topic, data.custom_format)

        #  write full report section by section
        sections = write_full_report(data.topic, research_result, plan)

        #  generate analysis and perspectives
        analysis = generate_critical_analysis(data.topic, research_result)
        perspectives = generate_perspectives(data.topic, research_result)

        # get references from researcher 
        references = research_result.get("references", [])

        return {
            "type": "research",
            "topic": data.topic,
            "domain": research_result.get("domain"),
            "source": research_result.get("source"),
            "sections": sections,
            "perspectives": perspectives,
            "critical_analysis": analysis,
            "references": references
        }

    except Exception as e:
        print("Generate report error:", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask-followup")
def ask_followup(data: FollowUpRequest):
    try:
        answer = answer_followup(data.question, data.report)
        return {
            "question": data.question,
            "answer": answer
        }
    except Exception as e:
        print("Followup error:", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/download-pdf")
def download_pdf(data: DownloadRequest):
    try:
        file_path = generate_pdf(data.topic, data.sections)

        if not os.path.exists(file_path):
            raise HTTPException(status_code=500, detail="PDF not generated")

        return FileResponse(
            path=file_path,
            filename="research_report.pdf",
            media_type="application/pdf"
        )

    except Exception as e:
        print("PDF error:", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/download-docx")
def download_docx(data: DownloadRequest):
    try:
        file_path = generate_docx(data.topic, data.sections)

        if not os.path.exists(file_path):
            raise HTTPException(status_code=500, detail="DOCX not generated")

        return FileResponse(
            path=file_path,
            filename="research_report.docx",
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    except Exception as e:
        print("DOCX error:", e)
        raise HTTPException(status_code=500, detail=str(e))
