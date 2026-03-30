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
        f"[{ref['id']}]({ref.get('url')}) {ref.get('title')}"
        for ref in references
        if ref.get("title") and ref.get("url")
    ])

    valid_ids = [str(ref["id"]) for ref in references]
    valid_ids_str = ", ".join(valid_ids)

    
    if section.lower() == "abstract":
        instruction = """
Write a concise synthesis of the research:
- Core problem
- Approach
- Key findings
- Why it matters
(No headings, no bullets)
"""
    elif section.lower() == "introduction":
        instruction = """
Explain the problem context, importance, and scope.
Clearly define the gap being addressed.
"""
    elif "literature" in section.lower():
        instruction = """
Compare existing approaches and findings.
Highlight agreements, contradictions, and trends.
"""
    elif "method" in section.lower():
        instruction = """
Explain how the problem is approached.
Focus on reasoning behind chosen methods.
"""
    elif "finding" in section.lower() or "result" in section.lower():
        instruction = """
Present key findings.
Focus on meaningful insights, not raw description.
"""
    elif "discussion" in section.lower():
        instruction = """
Interpret findings and explain implications.
Connect insights to real-world impact.
"""
    elif "conclusion" in section.lower():
        instruction = """
Summarize key insights and final takeaways.
Avoid repetition.
"""
    elif "future" in section.lower():
        instruction = """
Suggest realistic future research directions.
"""
    else:
        instruction = """
Provide analytical insights with reasoning and limitations.
"""

    
    prompt = f"""
You are an expert academic research analyst (NOT a summarizer).

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
- You SHOULD use citations whenever possible
- If references are provided, use them actively
- At least 1–2 citations must appear in each paragraph if relevant

STRICT VALIDATION:
- Allowed citations: [{valid_ids_str}]
- Any other citation is INVALID

INSTRUCTIONS:
{instruction}

REASONING RULES (VERY IMPORTANT):
- Do NOT copy or summarize sources directly
- Combine insights from multiple references
- Compare findings when possible
- Highlight patterns, contradictions, or gaps
- Explain WHY findings matter, not just WHAT they are
- Avoid generic phrases like "AI is transforming..."
- Avoid filler sentences

SYNTHESIS RULES (CRITICAL):
- Combine insights from multiple references into a single statement
- Identify overlapping findings across sources
- Merge similar ideas instead of repeating them
- Highlight agreement or contrast between sources
- Prefer fewer but stronger sentences

QUALITY RULES:
- Every paragraph must add new information
- Do NOT repeat ideas from previous sections
- Build on earlier content instead of restating
- Keep output concise but deep

CITATION RULES (VERY IMPORTANT):
- Use citations only when supporting a specific claim
- Prefer combining multiple sources when they support the same idea
- Combine citations like [1][2] for stronger evidence
- If two sources say similar things → merge into one sentence
- Do NOT write one sentence per reference
- Do NOT overuse citations

MANDATORY CITATION RULE:
- Every paragraph MUST include at least one citation if references exist
- Prefer combining citations like [1][2]
- Do NOT skip citations when references are available

HUMAN EXPERT STYLE (CRITICAL):
- Write like an experienced researcher explaining insights
- Use natural sentence flow, not rigid AI structure
- Vary sentence length (mix short + long sentences)
- Avoid repetitive phrasing patterns
- Do NOT sound like a template or checklist
- Use transitions between ideas (e.g., "however", "notably", "in contrast")
- Make reasoning feel intuitive, not mechanical

TONE:
- Confident but not exaggerated
- Analytical, not promotional
- Clear and readable

AVOID:
- robotic phrasing
- repetitive sentence starts
- over-structured or checklist-style writing

FORMAT:
- Use tables only when they improve clarity
- Prefer structured comparison over long paragraphs

STRICT OUTPUT RULE:
-Use tables STRICT OUTPUT RULE:
- DO NOT include sections like:
  "Correction"
  "Verification Notes"
  "Clarification"
  "Unsupported Claims"
- Write ONLY clean research content

EXAMPLES:

 Weak:
AI improves diagnosis [1]. Another study shows improvement [2].

 Strong:
AI improves diagnostic accuracy by leveraging pattern recognition across datasets [1][2].
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
- Be specific and analytical
- Avoid generic AI statements
- Focus on real weaknesses and trade-offs
"""

    return generate_text(prompt)