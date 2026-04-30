# AI Research Agent 

A multi-agent AI system that generates structured research reports using real-time data.

## Features
- Planner Agent (breaks topic into sections)
- Research Agent (web + PubMed integration)
- Writer Agent (generates structured report)
- Domain-aware routing
- PDF report generation

## Tech Stack
- FastAPI
- Python
- ReactJS
- OpenAI API
- PubMed API


## Run Locally
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload