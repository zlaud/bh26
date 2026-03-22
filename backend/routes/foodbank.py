import asyncio
from fastapi import APIRouter
from agents.foodbank_agent import run_foodbank_agent

router = APIRouter(prefix="/api/foodbank")

@router.get("/dashboard")
async def get_foodbank_dashboard(region: str = "national"):
    result = await asyncio.to_thread(run_foodbank_agent, region)
    return result or {"error": "Agent failed to produce results"}