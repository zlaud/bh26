from fastapi import APIRouter
from services.news_service import fetch_all_articles

router = APIRouter()

@router.post("/fetch-news")
async def fetch_news(days_back: int = 7):
    result = await fetch_all_articles(days_back=days_back)
    return result