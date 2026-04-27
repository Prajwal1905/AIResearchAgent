from app.services.llm import generate_text
from app.services.pdf_reader import extract_text_from_pdf


def explain_paper(file_path: str, topic: str = "") -> dict:
    
    
    paper_text = extract_text_from_pdf(file_path)

    if not paper_text or len(paper_text) < 200:
        return {"error": "Could not extract text from PDF. Make sure it is not a scanned image."}

   
    paper_text = paper_text[:6000]

    print("Extracting paper metadata...")

    
    meta_prompt = f"""
Read this research paper and extract:
1. Title
2. Authors (if visible)
3. Year (if visible)
4. Research question in one sentence
5. Main conclusion in one sentence

Paper:
{paper_text[:2000]}

Return as plain text with clear labels.
"""
    meta = generate_text(meta_prompt)

    print("Generating ELI5 explanation...")

    
    eli5_prompt = f"""
You are explaining a research paper to a 12-year-old with no science background.

Paper content:
{paper_text}

Explain this paper in the simplest possible way:
- What problem were they trying to solve? (use a simple analogy)
- What did they do to solve it? (no jargon)
- What did they find out?
- Why does it matter in everyday life?

Rules:
- Maximum 150 words
- No technical terms
- Use simple analogies like "it's like when..."
- Write like you're talking to a curious child
"""
    eli5 = generate_text(eli5_prompt)

    print("Generating student explanation...")

    
    student_prompt = f"""
You are explaining a research paper to an undergraduate student.

Paper content:
{paper_text}

Write a clear explanation covering:
- Background and why this research was needed
- Research question and hypothesis
- Methodology in plain English
- Key findings and what they mean
- How this connects to existing knowledge

Rules:
- 250-300 words
- Can use some technical terms but explain them
- Academic but accessible tone
- Focus on understanding not just summarizing
"""
    student = generate_text(student_prompt)

    print("Generating professional summary...")

   
    professional_prompt = f"""
You are writing an executive summary of a research paper for a busy professional.

Paper content:
{paper_text}

Write a professional summary covering:
- Core finding in one bold statement
- Evidence supporting it
- Business or practical implications
- Key numbers or statistics
- What decision-makers should know

Rules:
- 200 words maximum
- Lead with the most important finding
- Focus on implications not methodology
- Use bullet points for key facts
"""
    professional = generate_text(professional_prompt)

    print("Generating critical analysis...")

    
    analysis_prompt = f"""
You are a senior academic reviewer analyzing a research paper critically.

Paper content:
{paper_text}

Analyze this paper on these exact points:

### What This Paper Actually Proves
Be specific — what can we confidently conclude from this research?

### What This Paper Does NOT Prove
What are the limits of these conclusions? What cannot be generalized?

### Limitations the Authors Admit
What weaknesses do the authors themselves acknowledge?

### Real World Applications
How can these findings actually be used in practice?

### Questions This Paper Raises
What new research questions does this paper open up?

Be honest and specific. Avoid generic statements.
"""
    analysis = generate_text(analysis_prompt)

    print("Generating key quotes...")

    
    quotes_prompt = f"""
From this research paper, extract:
1. The 3 most important statistical findings or numbers
2. The most significant direct conclusion stated by the authors
3. The most important limitation mentioned

Paper:
{paper_text}

Format as a simple list. Be specific and quote actual numbers where possible.
"""
    key_facts = generate_text(quotes_prompt)

    return {
        "topic": topic,
        "meta": meta,
        "eli5": eli5,
        "student": student,
        "professional": professional,
        "analysis": analysis,
        "key_facts": key_facts,
    }
