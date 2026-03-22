from fastapi import APIRouter
from pydantic import BaseModel
from services.household_agent import run_household_agent
from services.impact_service import compute_collective_impact

router = APIRouter(prefix="/api/household")

class HouseholdRequest(BaseModel):
    groceries: str
    scale_id: str = "100_households"

class ImpactRequest(BaseModel):
    action_ids: list[str]
    scale_id: str = "100_households"

@router.post("/analyze")
async def analyze_household(request: HouseholdRequest):
    result = await run_household_agent(request.groceries, request.scale_id)
    return result

@router.post("/impact")
def get_collective_impact(request: ImpactRequest):
    return compute_collective_impact(request.action_ids, request.scale_id)