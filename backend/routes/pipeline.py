import asyncio
from fastapi import APIRouter
from services.news_service import fetch_all_articles
from services.signal_risk_agent import extract_all_signals
from services.risk_engine import compute_all_food_risks, compute_food_risks_with_injected_signal
from db.crud import get_all_articles, get_all_signals, get_all_food_risks
from pydantic import BaseModel
from agents.household_agent import run_household_agent
from services.json_loader import load_json

router = APIRouter(prefix="/api/pipeline")

@router.post("/fetch-news")
async def fetch_news(days_back: int = 7):
    return await fetch_all_articles(days_back=days_back)

@router.post("/extract-signals")
async def extract_signals():
    return await extract_all_signals()

@router.post("/compute-risks")
def compute_risks():
    risks = compute_all_food_risks()
    return {"computed": len(risks)}

@router.post("/run-all")
async def run_full_pipeline(days_back: int = 7):
    fetch_result = await fetch_all_articles(days_back=days_back)
    signal_result = await extract_all_signals()
    risk_result = compute_all_food_risks()
    return {
        "fetch": fetch_result,
        "signals": signal_result,
        "risks": {"computed": len(risk_result)}
    }

@router.get("/status")
def pipeline_status():
    return {
        "articles": len(get_all_articles()),
        "signals": len(get_all_signals()),
        "food_risks": len(get_all_food_risks())
    }

@router.get("/risks/global")
def get_global_risks():
    return {"risks": get_all_food_risks()}


class SimulateHeadlineRequest(BaseModel):
    groceries: str
    signal: dict
    scale_id: str = "100_households"

@router.post("/simulate-headline")
async def simulate_headline(request: SimulateHeadlineRequest):
    
    # Compute risks with injected signal
    risks = compute_food_risks_with_injected_signal(request.signal)
    
    # Run the household agent (sync function)
    result = await asyncio.to_thread(run_household_agent, request.groceries, request.scale_id)
    
    if result:
        # Override food_risks with the simulated risks
        groceries = load_json("groceries.json")
        valid_ids = {food["id"] for food in groceries["foods"]}
        label_to_id = {food["label"].lower(): food["id"] for food in groceries["foods"]}
        
        items = [item.strip().lower() for item in request.groceries.split(",") if item.strip()]
        user_foods = []
        for item in items:
            if item in valid_ids:
                user_foods.append(item)
            elif item in label_to_id:
                user_foods.append(label_to_id[item])
        
        result["food_risks"] = {f: risks[f] for f in user_foods if f in risks}
    
    return result or {"error": "Agent failed to produce results"}