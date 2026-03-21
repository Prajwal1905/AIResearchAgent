def get_research_prompt(topic: str) -> str:
    return f"""
You are an expert research assistant.

Generate a detailed and well-structured research report on the topic:
"{topic}"

Follow this exact structure:

1. Title
2. Abstract (short summary)
3. Introduction
4. Key Sections (with headings and explanations)
5. Conclusion

Make the content:
- Clear and professional
- Well formatted
- Easy to read
"""