from openai import OpenAI
from app.core.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)


def generate_text(prompt: str, system_prompt: str = "You are a helpful AI research assistant.") -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        return response.choices[0].message.content

    except Exception as e:
        print("LLM error:", e)
        return ""


def describe_image(base64_image: str, image_ext: str, caption: str = "", context: str = "") -> str:
    
    try:
        media_type = f"image/{image_ext}"
        if image_ext == "jpg":
            media_type = "image/jpeg"

        prompt_text = f"""Look carefully at this image and describe EXACTLY what you see.

Figure caption from document: {caption if caption else "Not provided"}

Instructions:
1. Read every text label, number, or annotation visible in the image
2. Describe every visual element — boxes, arrows, diagrams, charts, people, objects
3. Explain what each section or panel shows
4. If there are multiple examples or panels, describe each one separately
5. State specific details — object names, activity names, numbers shown

DO NOT guess or infer from outside knowledge.
ONLY describe what is literally visible in this image.
Be specific and detailed. Write 5-8 sentences."""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{media_type};base64,{base64_image}",
                                "detail": "high"  # use high detail mode for better accuracy
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt_text
                        }
                    ]
                }
            ],
            max_tokens=800
        )

        return response.choices[0].message.content

    except Exception as e:
        print("Vision LLM error:", e)
        return "Could not analyze this image."
