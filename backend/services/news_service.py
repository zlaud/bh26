import httpx
import os
import json
from db.crud import store_article, article_exists, get_all_articles
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.environ["NEWS_API_KEY"]
NEWS_API_URL = "https://eventregistry.org/api/v1/article/getArticles"

def load_query_library() -> list[dict]:
    with open("../data/query_library.json") as f:
        return json.load(f)["queries"]

async def fetch_articles_for_query(
    client: httpx.AsyncClient,
    query: dict,
    days_back: int = 7
) -> list[dict]:
    body = {
        "action": "getArticles",
        "keyword": query["query"],
        "articlesPage": 1,
        "articlesCount": 10,
        "articlesSortBy": "date",
        "articlesSortByAsc": False,
        "dataType": ["news"],
        "forceMaxDataTimeWindow": days_back,
        "resultType": "articles",
        "isDuplicateFilter": "skipDuplicates",
        "apiKey": NEWS_API_KEY
    }
    try:
        response = await client.post(NEWS_API_URL, json=body, timeout=15.0)
        response.raise_for_status()
        data = response.json()
        articles = data.get("articles", {}).get("results", [])
        print(f"Query {query['id']}: Found {len(articles)} articles")
        
        parsed = [
            {
                "title": a.get("title", "").strip(),
                "source": a.get("source", {}).get("title", ""),
                "url": a.get("url", ""),
                "published_at": a.get("dateTime", ""),
                "snippet": (a.get("body") or "")[:600].strip(),
                "query_id": query["id"],
                "event_type_hint": query["event_type"]
            }
            for a in articles
            if a.get("url") and a.get("title")
        ]
        
        if parsed:
            print(f"  Sample: {parsed[0]['title'][:60]}... from {parsed[0]['source']}")
        
        return parsed
    except httpx.HTTPStatusError as e:
        print(f"HTTP error for query {query['id']}: {e.response.status_code}")
        print(f"  Response: {e.response.text[:200]}")
        return []
    except Exception as e:
        print(f"Fetch error for query {query['id']}: {e}")
        return []

async def fetch_all_articles(days_back: int = 7) -> dict:
    queries = load_query_library()
    new_count = 0
    skipped = 0

    async with httpx.AsyncClient() as client:
        for query in queries:
            articles = await fetch_articles_for_query(client, query, days_back)
            for article in articles:
                if not article["url"]:
                    continue
                if article_exists(article["url"]):
                    skipped += 1
                else:
                    store_article(article)
                    new_count += 1
    return {
        "new": new_count,
        "skipped": skipped,
        "total": len(get_all_articles())
    }