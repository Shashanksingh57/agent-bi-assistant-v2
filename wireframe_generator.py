import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_wireframe_json_from_description(description: str) -> str:
    prompt = f"""You are a dashboard assistant. A wireframe layout was described as:

{description}

Return a JSON object with:
- layout_type: 'grid'
- sections: an array of objects each with:
  - zone
  - visual_title
  - visual_type

Only return valid JSON. No explanation."""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You convert layout sketches to structured JSON for dashboards."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=500
    )

    return response['choices'][0]['message']['content']