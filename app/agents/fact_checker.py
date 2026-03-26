from app.services.llm import generate_text


def fact_check_section(topic: str, section: str, content: str, research_data: list):
    
    try:
        
        context_list = []
        for item in research_data:
            if isinstance(item, dict):
                context_list.append(item.get("summary", ""))
            else:
                context_list.append(str(item))

        context = "\n".join(context_list)

        prompt = f"""
You are a strict academic fact-checker.

Topic: {topic}
Section: {section}

Content to verify:
{content}

Reference data:
{context}

Tasks:
1. Identify incorrect or unsupported claims
2. Correct them using reference data
3. Improve factual clarity

Rules:
- Do NOT rewrite everything
- Keep structure same
- Be precise
"""

        result = generate_text(prompt)

       
        if not result or len(result.strip()) < 20:
            return content

        return result

    except Exception as e:
        print("FACT CHECK ERROR:", e)
        return content  