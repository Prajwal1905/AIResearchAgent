from app.services.llm import generate_text


def write_section(
    topic: str,
    section: str,
    research_result: dict,
    previous_content: str = ""
) -> str:

    domain = research_result.get("domain", "General")
    references = research_result.get("references", [])

    ref_text = "\n".join([
        f"[{ref['id']}] {ref.get('title')}"
        for ref in references
        if ref.get("title")
    ])

   
    valid_ids = [str(ref["id"]) for ref in references]
    valid_ids_str = ", ".join(valid_ids)

    
    if section.lower() == "abstract":
        instruction = """
Write a concise summary of the entire research.
Include:
- Problem
- Approach
- Key findings
- Importance
(No headings, no bullets)
"""
    elif section.lower() == "introduction":
        instruction = """
Explain background, importance, and scope of the topic.
Set context clearly and define problem space.
"""
    elif "literature" in section.lower():
        instruction = """
Review existing research and compare different approaches.
Highlight trends, agreements, and disagreements.
"""
    elif "method" in section.lower():
        instruction = """
Explain how the problem can be approached.
Discuss models, frameworks, or methodologies used.
"""
    elif "finding" in section.lower() or "result" in section.lower():
        instruction = """
Present key findings derived from research.
Focus on evidence and outcomes.
"""
    elif "discussion" in section.lower():
        instruction = """
Interpret findings and explain implications.
Connect results with real-world meaning.
"""
    elif "conclusion" in section.lower():
        instruction = """
Summarize key insights and overall takeaway.
Do NOT repeat earlier text.
"""
    elif "future" in section.lower():
        instruction = """
Suggest future research directions and improvements.
"""
    else:
        instruction = """
Write analytical content using evidence, insights, and limitations.
"""

    
    prompt = f"""
You are an expert academic research writer.

Topic: {topic}
Section: {section}
Domain: {domain}

Previously written content:
{previous_content}

Available References:
{ref_text}

IMPORTANT:
- You MUST ONLY use these reference IDs: {valid_ids_str}
- DO NOT generate any other citations
- DO NOT use [5], [10], etc if not listed
- If unsure, DO NOT add citation

STRICT VALIDATION:
- Allowed citations: [{valid_ids_str}]
- Any other citation is INVALID

Instructions:
{instruction}

RULES:
- Use only given references
- Cite naturally like [1], [2]
- Do NOT invent citations
- Be analytical and precise
- Avoid repetition

FORMAT:
- Use tables where useful
- Keep clarity over verbosity
"""

    return generate_text(prompt)


def generate_critical_analysis(topic: str, research_result: dict):
    data = research_result.get("data", [])
    context = "\n".join([str(item) for item in data])

    prompt = f"""
You are a senior research reviewer.

Topic: {topic}

Based on this data:
{context}

Write a deep critical analysis:

1. Key Limitations (methodological + data issues)
2. Risks & Challenges (real-world + technical)
3. Biases & Gaps (dataset, assumptions, missing perspectives)

Rules:
- Be specific, not generic
- Think like a peer reviewer
- Avoid repeating general statements
"""

    return generate_text(prompt)