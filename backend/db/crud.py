from db.database import articles_col, signals_col, food_risks_col
from utils.hashing import hash_url
from datetime import datetime, timezone

def store_article(article: dict) -> tuple[str, bool]:
    article_id = hash_url(article["url"])
    result = articles_col.update_one(
        {"url": article["url"]},
        {
            "$setOnInsert": {
                **article,
                "_id": article_id,
                "id": article_id,
                "cached_at": datetime.now(timezone.utc).isoformat(),
                "embedding": []
            }
        },
        upsert=True
    )
    is_new = result.upserted_id is not None
    return article_id, is_new

def get_all_articles() -> list[dict]:
    return list(
        articles_col.find({}, {"_id": 0}).sort("cached_at", -1)
    )

def update_article_embedding(article_id: str, embedding: list[float]):
    articles_col.update_one(
        {"_id": article_id},
        {"$set": {"embedding": embedding}}
    )

def find_similar_articles(query_embedding: list[float], top_k: int = 5) -> list[dict]:
    if not query_embedding:
        return []
    
    pipeline = [
        {
            "$vectorSearch": {
                "index": "article_embeddings",
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": 100,
                "limit": top_k
            }
        },
        {
            "$project": {
                "_id": 0,
                "id": 1,
                "title": 1,
                "source": 1,
                "snippet": 1,
                "published_at": 1,
                "event_type_hint": 1,
                "score": {"$meta": "vectorSearchScore"}
            }
        }
    ]
    return list(articles_col.aggregate(pipeline))

def signal_exists(article_id: str) -> bool:
    # check if ANY signal exists for this base article_id
    base_id = article_id.split("_")[0] if "_" in article_id else article_id
    return signals_col.find_one(
        {"article_id": {"$regex": f"^{base_id}"}},
        {"_id": 1}
    ) is not None

def store_signal(article_id: str, signal: dict):
    if signal_exists(article_id):
        return
    signals_col.insert_one({
        **signal,
        "article_id": article_id,
        "extracted_at": datetime.now(timezone.utc).isoformat()
    })

def get_all_signals() -> list[dict]:
    return list(signals_col.find({}, {"_id": 0}))

def upsert_food_risk(risk: dict):
    food_risks_col.update_one(
        {"food": risk["food"]},
        {"$set": {
            **risk,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }},
        upsert=True
    )

def get_all_food_risks() -> dict:
    risks = list(food_risks_col.find({}, {"_id": 0}))
    return {r["food"]: r for r in risks}