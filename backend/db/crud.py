from db.database import articles_col
from utils.hashing import hash_url
from datetime import datetime, timezone

def article_exists(url: str) -> bool:
    return articles_col.find_one({"url": url}, {"_id": 1}) is not None

def store_article(article: dict) -> str:
    article_id = hash_url(article["url"])
    if article_exists(article["url"]):
        return article_id
    articles_col.insert_one({
        **article,
        "_id": article_id,
        "id": article_id,
        "cached_at": datetime.now(timezone.utc).isoformat(),
        "embedding": []
    })
    return article_id

def get_all_articles() -> list[dict]:
    return list(
        articles_col.find({}, {"_id": 0}).sort("cached_at", -1)
    )