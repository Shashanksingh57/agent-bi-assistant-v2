from schemas import DashboardRequest
from utils import build_prompt_from_payload
from llm_client import call_llm

def generate_instructions(payload: DashboardRequest):
    prompt = build_prompt_from_payload(payload)
    instructions_text = call_llm(prompt)
    
    # If you want to return a list instead of raw text
    instruction_steps = [step.strip() for step in instructions_text.split('\n') if step.strip()]
    
    return instruction_steps