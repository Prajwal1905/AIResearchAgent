from app.services.llm import generate_text
from app.services.pdf_reader import extract_text_from_multiple_pdfs


def generate_literature_review(topic: str, file_paths: list) -> dict:
    """
    Generate a full academic literature review from uploaded PDF papers.

    Args:
        topic: The research topic
        file_paths: List of paths to uploaded PDF files

    Returns:
        dict with sections, gaps, research questions, references
    """

    
    papers = extract_text_from_multiple_pdfs(file_paths)

    if not papers:
        return {
            "error": "Could not extract text from uploaded PDFs. Make sure files are not scanned images."
        }

    print(f"Processing {len(papers)} papers for literature review")

    papers_context = ""
    for i, paper in enumerate(papers, start=1):
        papers_context += f"\n\nPaper [{i}] — {paper['filename']}:\n{paper['text'][:3000]}"

    # generate individual paper summaries first
    summaries = []
    for i, paper in enumerate(papers, start=1):
        summary_prompt = f"""
Summarize this academic paper in 3-4 sentences covering:
- Main research question
- Methodology used
- Key findings
- Limitations

Paper: {paper['text'][:3000]}
"""
        summary = generate_text(summary_prompt)
        summaries.append({
            "id": i,
            "filename": paper["filename"],
            "summary": summary
        })
        print(f"Summarized paper {i}/{len(papers)}")

    
    summaries_text = "\n\n".join([
        f"[{s['id']}] {s['filename']}:\n{s['summary']}"
        for s in summaries
    ])

    
    review_prompt = f"""
You are an expert academic researcher writing a literature review.

Research Topic: {topic}

Here are summaries of {len(papers)} papers:

{summaries_text}

Write a comprehensive literature review with these sections:

### Overview
Summarize the overall state of research on this topic.

### Key Themes
Identify 3-4 major themes that emerge across the papers.

### Agreements
What do most papers agree on? What is well established?

### Contradictions and Debates
Where do papers disagree? What is still debated?

### Methodological Approaches
What methods are commonly used? What are their strengths and weaknesses?

### Research Gaps
What questions remain unanswered? What has not been studied yet?

### Future Directions
What should future research focus on?

Rules:
- Use citations like [1][2] throughout
- Be analytical not just descriptive
- Compare and contrast papers directly
- Write in academic tone
- Minimum 800 words
"""

    system_prompt = "You are an expert academic researcher who writes rigorous, analytical literature reviews."
    review_text = generate_text(review_prompt, system_prompt=system_prompt)

    
    rq_prompt = f"""
Based on this literature review on "{topic}", generate:

1. 5 strong research questions that could form the basis of a new study
2. 3 hypotheses that could be tested
3. Suggested research methodology for the most important gap

Keep it concise and specific.

Literature review summary:
{summaries_text}
"""
    research_questions = generate_text(rq_prompt)

    
    references = [
        {
            "id": s["id"],
            "title": s["filename"].replace(".pdf", ""),
            "url": "",
            "source": "uploaded"
        }
        for s in summaries
    ]

    return {
        "topic": topic,
        "paper_count": len(papers),
        "summaries": summaries,
        "review": review_text,
        "research_questions": research_questions,
        "references": references
    }
