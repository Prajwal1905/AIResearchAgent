from app.services.llm import generate_text
from app.services.pdf_reader import extract_text_from_pdf


def explain_paper(file_path: str, topic: str = "", level: str = "student") -> dict:
    
    paper_text = extract_text_from_pdf(file_path)

    if not paper_text or len(paper_text) < 200:
        return {"error": "Could not extract text from PDF. Make sure it is not a scanned image."}

    paper_text = paper_text[:6000]

    print(f"Explaining paper at level: {level}")

   
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

    explanation = ""
    analysis = ""
    key_facts = ""

    if level == "eli5":
        prompt = f"""
You are explaining a research paper to a 12-year-old with no science background.

Paper:
{paper_text}

Explain this paper in the simplest possible way:
- What problem were they trying to solve? (use a simple analogy)
- What did they do to solve it? (no jargon at all)
- What did they find out?
- Why does it matter in everyday life?

Rules:
- Maximum 200 words
- No technical terms
- Use analogies like "it's like when..."
- Write like talking to a curious child
"""
        explanation = generate_text(prompt)

    elif level == "student":
        prompt = f"""
You are explaining a research paper to an undergraduate student.

Paper:
{paper_text}

Write a clear explanation covering:
- Background and why this research was needed
- Research question and hypothesis
- Methodology in plain English
- Key findings and what they mean
- How this connects to existing knowledge

Rules:
- 300-400 words
- Can use technical terms but explain them briefly
- Academic but accessible tone
"""
        explanation = generate_text(prompt)

    elif level == "professional":
        prompt = f"""
You are writing an executive summary of a research paper for a busy professional.

Paper:
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
- Use bullet points for key facts
- Focus on implications not methodology
"""
        explanation = generate_text(prompt)

    elif level == "full":
        
        student_prompt = f"""
You are explaining a research paper to an undergraduate student.

Paper:
{paper_text}

Write a clear explanation covering:
- Background and why this research was needed
- Research question and hypothesis  
- Methodology in plain English
- Key findings and what they mean
- How this connects to existing knowledge

Rules:
- 300-400 words
- Academic but accessible tone
"""
        explanation = generate_text(student_prompt)

        analysis_prompt = f"""
You are a senior academic reviewer analyzing a research paper.

Paper:
{paper_text}

Analyze this paper on these points:

### What This Paper Actually Proves
What can we confidently conclude?

### What This Paper Does NOT Prove
What are the limits of these conclusions?

### Limitations the Authors Admit
What weaknesses do the authors acknowledge?

### Real World Applications
How can findings be used in practice?

### Questions This Paper Raises
What new research questions does it open?

Be specific and honest. Avoid generic statements.
"""
        analysis = generate_text(analysis_prompt)

        facts_prompt = f"""
From this research paper extract:
1. The 3 most important statistical findings or numbers
2. The most significant conclusion stated by the authors
3. The most important limitation mentioned

Paper:
{paper_text}

Format as a simple numbered list. Quote actual numbers where possible.
"""
        key_facts = generate_text(facts_prompt)

    return {
        "topic": topic,
        "level": level,
        "meta": meta,
        "explanation": explanation,
        "analysis": analysis,
        "key_facts": key_facts,
    }
