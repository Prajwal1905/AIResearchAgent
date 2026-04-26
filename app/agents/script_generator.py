from app.services.llm import generate_text
from app.services.research_router import route_research


def generate_script(topic: str, style: str = "educational") -> dict:
    """
    Generate a full YouTube script for a given topic.
    style options: educational, entertainment, documentary, tutorial
    """

    # first research the topic
    research_result = route_research(topic)
    data = research_result.get("data", [])

    # build context from research
    context = "\n".join([
        f"- {item.get('title')}: {item.get('summary', '')}"
        for item in data
        if item.get("summary")
    ])

    references = research_result.get("references", [])
    ref_text = "\n".join([
        f"[{ref['id']}] {ref.get('title')} - {ref.get('url')}"
        for ref in references
        if ref.get("title")
    ])

    prompt = f"""
You are an expert YouTube scriptwriter and researcher.

Topic: {topic}
Style: {style}

Research data:
{context}

References:
{ref_text}

Write a complete, engaging YouTube script with these exact sections:

HOOK (first 30 seconds — grab attention immediately, ask a bold question or share a shocking fact)

INTRODUCTION (introduce yourself and what viewers will learn today)

BACKGROUND (give context — why this topic matters right now)

MAIN POINT 1 (first key insight with evidence)

MAIN POINT 2 (second key insight with evidence)

MAIN POINT 3 (third key insight with evidence)

EXAMPLES AND CASE STUDIES (real world examples that make it concrete)

COUNTERARGUMENTS (address what skeptics say — makes content more credible)

KEY TAKEAWAYS (summarize the 3 most important points)

CALL TO ACTION (tell viewers to like, subscribe, comment their thoughts)

Rules:
- Write conversationally, like you are talking to the viewer
- Use short punchy sentences
- Add [PAUSE] where presenter should pause for effect
- Add [B-ROLL: description] where visuals should change
- Include actual facts and statistics from the research
- Hook must be under 30 seconds when read aloud
- Total script should be 8-12 minutes when read aloud (around 1200-1800 words)
- Use citations like [1][2] when stating facts
"""

    system_prompt = "You are an expert YouTube scriptwriter who creates viral, well-researched educational content."
    script_text = generate_text(prompt, system_prompt=system_prompt)

    # generate title and thumbnail ideas separately
    meta_prompt = f"""
Topic: {topic}

Generate:
1. 5 viral YouTube title options (use numbers, questions, or shocking statements)
2. 3 thumbnail text ideas (very short, max 4 words each)
3. 5 relevant hashtags
4. Best time to post (day and time)

Return as plain text with clear labels.
"""
    meta = generate_text(meta_prompt)

    return {
        "topic": topic,
        "style": style,
        "script": script_text,
        "meta": meta,
        "references": references,
        "domain": research_result.get("domain", "general")
    }
