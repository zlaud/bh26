from db.database import articles_col
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