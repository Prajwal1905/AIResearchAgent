from app.services.llm import generate_text


def write_section(
    topic: str,
    section: str,
    research_result: dict,
    previous_content: str = ""
) -> str:

    domain = research_result.get("domain", "General")
    data = research_result.get("data", [])

    
    ref_text = "\n".join([
        f"[{i+1}] {item.get('title')}- {item.get('url')}"
        for i, item in enumerate(data)
        if item.get("title") and item.get("url")
    ])

    
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

Available References (USE THESE EXACT IDS ONLY):
{ref_text}

IMPORTANT:
- You MUST ONLY use the reference IDs provided above
- DO NOT invent [1], [2], etc.
- Each citation must match EXACTLY the given references
- If unsure, do NOT add citation

Instructions:
{instruction}

STRICT RULES:
- Use ONLY the given references
- Cite using [1], [2], etc.
- Do NOT invent citations
- Every major claim must have a citation
- Avoid unsupported numbers like % unless from references
- Be analytical and precise
- No repetition

FORMAT RULES:
- Use structured tables where possible
- Prefer comparison tables over long text

VERIFICATION RULES:
 Verified Insight:
- Must be supported by references [1], [2]

 Assumed / Theoretical:
- Based on reasoning or inference
- Use when no direct citation exists

- Clearly separate both types
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
- Avoid repeating general AI statements
"""

    return generate_text(prompt)