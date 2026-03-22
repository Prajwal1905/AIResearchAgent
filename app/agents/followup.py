from app.services.llm import generate_text


def answer_followup(question: str, report: dict):
    context = ""

    for section, content in report["sections"].items():
        context += f"\n{section}:\n{content}\n"

    context += f"\nCritical Analysis:\n{report.get('critical_analysis', '')}"
 

    prompt = f"""
You are an expert research assistant.

Here is the previous research report:
{context}

User question:
{question}

Instructions:
- Answer based ONLY on the report
- Keep it clear and detailed
- If possible, refer to evidence using [1], [2]
- Do NOT introduce new information
- If simplifying, keep meaning intact

Answer:
"""
    
    return generate_text(prompt)