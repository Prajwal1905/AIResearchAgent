from app.services.llm import generate_text


def format_references(data):
    references = []
    for i, item in enumerate(data, start=1):
        ref = f"[{i}] {item.get('title')} - {item.get('source')} ({item.get('date')})"
        references.append(ref)
    return references


def write_section(topic: str, section: str, research_result: dict) -> str:
    domain = research_result["domain"]
    source = research_result["source"]
    data = research_result["data"]

    references = format_references(data)
    ref_text = "\n".join(references)

    prompt = f"""
You are an expert research analyst.

Topic: {topic}
Section: {section}
Domain: {domain}

Use the following references:
{ref_text}

Write in this structured format:

 Evidence:
- Use factual points with citations like [1], [2]

 Key Insights:
- Explain what the evidence means

 Recommendations:
- Provide practical suggestions or decisions

 Limitations:
- Mention gaps, risks, or uncertainties

Rules:
- Be specific and non-generic
- Always use references
- Keep it analytical, not descriptive
- Prefer higher credibility sources when generating insights
"""

    return generate_text(prompt)

def generate_critical_analysis(topic: str, research_result: dict):
    data = research_result["data"]

    context = "\n".join([str(item) for item in data])

    prompt = f"""
You are a critical research analyst.

Topic: {topic}

Based on the following research data:
{context}

Write:
- Key limitations of current research
- Risks or challenges
- Bias or gaps

Be clear, honest, and analytical.
"""

    return generate_text(prompt)