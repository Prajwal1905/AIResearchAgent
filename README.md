# Synthex — AI Research Platform

A full-stack AI platform that automates research, writing and document analysis across multiple modes.

---

## Features

| Mode | What it does |
|---|---|
| **Research Paper** | Generates full academic papers with citations, critical analysis and perspectives on any topic |
| **YouTube Script** | Creates fully researched scripts with hook, main points, B-roll markers and title ideas |
| **Literature Review** | Upload multiple PDFs and get themes, contradictions, gaps and research questions |
| **Explain Paper** | Upload any research paper and get ELI5, Student, Professional or Full Analysis explanation |
| **Chat With File** | Upload any document and ask questions — supports PDF, DOCX, PPTX, XLSX, CSV, TXT, EPUB |

---

## Tech Stack

**Backend**
- Python, FastAPI
- OpenAI GPT-4o-mini (text), GPT-4o (vision)
- Tavily Search API
- PubMed API (medical research)
- ArXiv API (AI/CS/science papers)
- PyMuPDF, python-docx, python-pptx, openpyxl

**Frontend**
- React, Vite, Tailwind CSS
- ReactMarkdown with citation rendering
- localStorage for persistent chat history

---



---

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/ai-research-agent.git
cd ai-research-agent
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate        
source venv/bin/activate     
```

### 3. Install Python dependencies
```bash
pip install fastapi uvicorn openai python-dotenv beautifulsoup4 requests
pip install pymupdf python-docx python-pptx openpyxl
pip install python-multipart tavily-python reportlab
```

### 4. Set up environment variables
Create a `.env` file in the root folder:
```
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
```

### 5. Install frontend dependencies
```bash
cd ai-research-ui
npm install
```

---

## Running the App

**Terminal 1 — Backend:**
```bash
uvicorn app.main:app --reload
```

**Terminal 2 — Frontend:**
```bash
cd ai-research-ui
npm run dev
```

Open **http://localhost:5173** in your browser.

---

## API Routes

| Method | Route | Description |
|---|---|---|
| POST | `/generate-report` | Generate full research paper |
| POST | `/generate-script` | Generate YouTube script |
| POST | `/generate-literature-review` | Literature review from PDFs |
| POST | `/explain-paper` | Explain paper at chosen level |
| POST | `/upload-pdf-chat` | Upload file for chat |
| POST | `/chat-with-pdf` | Ask questions about uploaded file |
| POST | `/ask-followup` | Follow-up question on report |
| POST | `/download-pdf` | Download report as PDF |
| POST | `/download-docx` | Download report as Word |

---

## How Research Routing Works

```
User enters topic
       ↓
ai_classifier.py — keyword matching + LLM fallback
       ↓
Medical/Health    →  PubMed API
AI/CS/Physics     →  ArXiv API
Everything else   →  Tavily Search
       ↓
Scrape + Summarize sources
       ↓
Sort by credibility score
       ↓
Top 5 sources → Write report section by section
```

---

## API Keys

| Key | Where to get | Free? |
|---|---|---|
| `OPENAI_API_KEY` | platform.openai.com | Pay per use |
| `TAVILY_API_KEY` | tavily.com | 1000 free/month |

---

## License

MIT
