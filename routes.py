from fastapi import APIRouter
from schemas import DashboardRequest
from services import generate_instructions

router = APIRouter()

@router.post("/generate-instructions")
async def create_instructions(payload: DashboardRequest):
    instructions = generate_instructions(payload)
    return {"instructions": instructions}