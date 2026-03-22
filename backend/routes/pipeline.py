from fastapi import APIRouter
from services.news_service import fetch_all_articles
from services.signal_risk_agent import extract_all_signals
from services.risk_engine import compute_all_food_risks
from db.crud import get_all_articles, get_all_signals, get_all_food_risks

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