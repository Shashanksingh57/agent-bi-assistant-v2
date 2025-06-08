# layout_router.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os, json, requests
from dotenv import load_dotenv

load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

router = APIRouter(prefix="/api/v1", tags=["layout"])


class LayoutRequest(BaseModel):
    sketch_description: str = ""
    platform_selected: str = "Power BI"
    custom_prompt: str = None
    model_metadata: dict = None
    include_data_prep: bool = False
    data_prep_only: bool = False


class SprintRequest(BaseModel):
    wireframe_json: dict
    layout_instructions: str
    sprint_length_days: int
    velocity: int


def openai_chat_completion(payload: dict) -> dict:
    """
    Call OpenAI's chat completions endpoint with SSL verification disabled.
    """
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_KEY}",
        "Content-Type": "application/json"
    }
    resp = requests.post(url, headers=headers, json=payload, verify=False)
    resp.raise_for_status()
    return resp.json()


@router.post("/generate-layout")
def generate_layout(layout: LayoutRequest):
    try:
        # --- Data‑prep only branch ---
        if layout.data_prep_only:
            schema = json.dumps(layout.model_metadata or {}, indent=2)
            prompt = (
                "You are a Power BI expert. Given this schema, generate numbered Power Query M steps:\n\n"
                f"{schema}\n\n"
                "Include null handling for each numeric column, date conversion for each date column, "
                "and instructions to set up relationships."
            )
            body = {
                "model": "gpt-4",
                "messages": [
                    {"role": "system", "content": "Generate Power Query data‑prep instructions."},
                    {"role": "user",   "content": prompt}
                ],
                "temperature": 0.2,
                "max_tokens": 500
            }
            result = openai_chat_completion(body)
            text = result["choices"][0]["message"]["content"]
            return {"layout_instructions": text}

        # --- Full flow: wireframe + build instructions ---

        # 1) Wireframe JSON
        body1 = {
            "model": "gpt-4",
            "messages": [
                {"role": "system",  "content": "Convert layout sketches to JSON wireframes."},
                {"role": "user",    "content":
                    "Convert this sketch to JSON wireframe:\n\n"
                    + layout.sketch_description
                    + "\n\nReturn only valid JSON with layout_type and sections."
                }
            ],
            "temperature": 0.3,
            "max_tokens": 600
        }
        resp1 = openai_chat_completion(body1)
        wireframe_json = resp1["choices"][0]["message"]["content"]

        # 2) Build instructions
        parts = [
            f"Build instructions for {layout.platform_selected}.",
            "Wireframe JSON:", wireframe_json,
            "User context:", layout.custom_prompt or "[None]"
        ]
        if layout.platform_selected.lower() == "tableau":
            parts.append("Use Tableau terminology and recommend Tableau Prep if needed.")
        if layout.model_metadata:
            parts.append("Schema metadata:\n" + json.dumps(layout.model_metadata, indent=2))
        parts.append("Now return step-by-step build instructions for placement, measures, and styling.")

        body2 = {
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": "Generate dashboard build instructions."},
                {"role": "user",   "content": "\n\n".join(parts)}
            ],
            "temperature": 0.3,
            "max_tokens": 800
        }
        resp2 = openai_chat_completion(body2)
        instructions = resp2["choices"][0]["message"]["content"]

        return {
            "wireframe_json": wireframe_json,
            "layout_instructions": instructions
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-sprint")
def generate_sprint(req: SprintRequest):
    try:
        prompt = (
            "You are an agile planning assistant. Given the wireframe and instructions, "
            "generate a JSON sprint backlog strictly as valid JSON:\n\n"
            f"Wireframe JSON:\n{json.dumps(req.wireframe_json, indent=2)}\n\n"
            f"Build Instructions:\n{req.layout_instructions}\n\n"
            f"Sprint Length: {req.sprint_length_days} days, Velocity: {req.velocity} points\n\n"
            "Output ONLY the JSON object with keys: sprint_stories, total_estimated_points, velocity, over_under_capacity."
        )
        body = {
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": "Generate an agile sprint backlog JSON."},
                {"role": "user",   "content": prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 700
        }
        resp = openai_chat_completion(body)
        content = resp["choices"][0]["message"]["content"].strip()

        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail=f"Invalid JSON from model:\n{content}")

        return data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
