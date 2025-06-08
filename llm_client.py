from dotenv import load_dotenv
import os
import openai

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def call_llm(prompt: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # or gpt-4 if you have access
        messages=[
            {"role": "system", "content": "You are a dashboard assistant that generates step-by-step dashboard building instructions."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=2000
    )
    content = response['choices'][0]['message']['content']
    
    if not content.strip():
        return "No instructions generated. Please retry with a simpler request."

    return content