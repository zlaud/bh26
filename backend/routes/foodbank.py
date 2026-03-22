from fastapi import APIRouter
from services.foodbank_agent import run_foodbank_agent

router = APIRouter(prefix="/api/foodbank")

@router.get("/dashboard")
async def get_foodbank_dashboard(region: str = "national"):
    return await run_foodbank_agent(region=region)