from app.services.llm import generate_text


def get_section_instruction(section: str) -> str:

    section_lower = section.lower()

    if section_lower == "abstract":
        return "Write a concise summary: core problem, approach, key findings, and why it matters. No headings or bullets."

    elif section_lower == "introduction":
        return "Explain the problem context, importance, and scope. Define the gap being addressed."

    elif "literature" in section_lower:
        return "Compare existing approaches and findings. Highlight agreements, contradictions, and trends."

    elif "method" in section_lower:
        return "Explain how the problem is approached. Focus on reasoning behind chosen methods."

    elif "finding" in section_lower or "result" in section_lower:
        return "Present key findings. Focus on meaningful insights, not raw description."

    elif "discussion" in section_lower:
        return "Interpret findings and explain implications. Connect insights to real-world impact."

    elif "conclusion" in section_lower:
        return "Summarize key insights and final takeaways. Avoid repetition."

    elif "future" in section_lower:
        return "Suggest realistic future research directions."

    else:
        return "Provide analytical insights with reasoning and limitations."


def write_section(topic: str, section: str, research_result: dict, previous_content: str = "") -> str:

    domain = research_result.get("domain", "General")
    references = research_result.get("references", [])

  
    ref_text = "\n".join([
        f"[{ref['id']}] {ref.get('title')} - {ref.get('url')}"
        for ref in references
        if ref.get("title") and ref.get("url")
    ])

    valid_ids = ", ".join([str(ref["id"]) for ref in references])
    instruction = get_section_instruction(section)

    prompt = f"""
You are an expert academic research analyst.

Topic: {topic}
Section: {section}
Domain: {domain}

Previously written content (do not repeat this):
{previous_content}

Available References:
{ref_text}

Instructions for this section:
{instruction}

Rules:
- Use ONLY these citation IDs: {valid_ids}
- Combine insights from multiple references
- Write like a real researcher, not a template
- Every paragraph must have at least one citation if references exist
- Use citations like [1][2] when two sources agree
- Do NOT copy source text directly
- Avoid generic phrases like "AI is transforming..."

Write the {section} section now:
"""

    system_prompt = "You are an expert academic research analyst who writes clear, analytical research papers."

    return generate_text(prompt, system_prompt=system_prompt)


def generate_critical_analysis(topic: str, research_result: dict) -> str:

    data = research_result.get("data", [])

    
    context = "\n".join([
        f"- {item.get('title')}: {item.get('summary', '')}"
        for item in data
    ])

    prompt = f"""
You are a senior research reviewer.

Topic: {topic}

Research data:
{context}

Write a critical analysis covering:
1. Key Limitations (methodological and data issues)
2. Risks and Challenges (real-world and technical)
3. Biases and Gaps (missing perspectives or assumptions)

Rules:
- Be specific and analytical
- Avoid generic statements
- Focus on real weaknesses and trade-offs
"""

    return generate_text(prompt)


def write_full_report(topic: str, research_result: dict, plan: list = None) -> dict:


    if not plan:
        plan = [
            "Abstract",
            "Introduction",
            "Literature Review",
            "Methodology",
            "Findings",
            "Discussion",
            "Conclusion",
            "Future Work"
        ]

    report = {}
    previous_content = ""

    for section in plan:
        print(f"Writing section: {section}")

        content = write_section(topic, section, research_result, previous_content)
        report[section] = content

        
        previous_content += f"\n{section}: {content[:300]}"

    return report
