from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import List, Union
import os
import shutil
import uuid

from app.schemas.request import (
    TopicRequest,
    FollowUpRequest,
    DownloadRequest,
    ScriptRequest
)
from app.agents.writer import write_full_report, generate_critical_analysis
from app.agents.researcher import research_topic
from app.agents.followup import answer_followup
from app.agents.perspective import generate_perspectives
from app.agents.comparator import compare_topics
from app.agents.planner import create_plan
from app.agents.script_generator import generate_script
from app.agents.literature_reviewer import generate_literature_review
from app.agents.paper_explainer import explain_paper
from app.utils.pdf_generator import generate_pdf
from app.utils.docx_generator import generate_docx


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
def home():
    return {"message": "Synthex AI Platform is running"}


@app.post("/generate-report")
async def generate_report(data: TopicRequest):
    try:
        if " vs " in data.topic.lower():
            comparison = compare_topics(data.topic)
            return {"topic": data.topic, "type": "comparison", "result": comparison}

        try:
            research_result = research_topic(data.topic)
        except Exception as e:
            print("Research error:", e)
            research_result = {"domain": "General", "source": "Fallback", "data": [], "references": []}

        plan = create_plan(data.topic, data.custom_format)
        sections = write_full_report(data.topic, research_result, plan)
        analysis = generate_critical_analysis(data.topic, research_result)
        perspectives = generate_perspectives(data.topic, research_result)
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


@app.post("/generate-script")
async def generate_script_route(data: ScriptRequest):
    try:
        result = generate_script(data.topic, data.style)
        return {"type": "script", **result}
    except Exception as e:
        print("Script error:", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-literature-review")
async def generate_literature_review_route(
    topic: str = Form(...),
    files: List[UploadFile] = File(...)
):
    try:
        saved_paths = []
        for file in files:
            if not file.filename.endswith(".pdf"):
                continue
            unique_name = f"{uuid.uuid4()}_{file.filename}"
            file_path = os.path.join(UPLOAD_DIR, unique_name)
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            saved_paths.append(file_path)

        if not saved_paths:
            raise HTTPException(status_code=400, detail="Please upload at least one PDF file")

        result = generate_literature_review(topic, saved_paths)

        for path in saved_paths:
            try:
                os.remove(path)
            except Exception:
                pass

        return {"type": "literature_review", **result}

    except Exception as e:
        print("Literature review error:", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/explain-paper")
async def explain_paper_route(
    topic: str = Form(""),
    level: str = Form("student"),
    file: UploadFile = File(...)
):
    try:
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Please upload a PDF file")

        unique_name = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, unique_name)

        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        result = explain_paper(file_path, topic, level)

        try:
            os.remove(file_path)
        except Exception:
            pass

        return {"type": "paper_explainer", **result}

    except Exception as e:
        print("Paper explainer error:", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask-followup")
def ask_followup(data: FollowUpRequest):
    try:
        answer = answer_followup(data.question, data.report)
        return {"question": data.question, "answer": answer}
    except Exception as e:
        print("Followup error:", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/download-pdf")
def download_pdf(data: DownloadRequest):
    try:
        file_path = generate_pdf(data.topic, data.sections)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=500, detail="PDF not generated")
        return FileResponse(path=file_path, filename="report.pdf", media_type="application/pdf")
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
            path=file_path, filename="report.docx",
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    except Exception as e:
        print("DOCX error:", e)
        raise HTTPException(status_code=500, detail=str(e))
