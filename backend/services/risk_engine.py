import json
from db.crud import get_all_signals, upsert_food_risk, get_all_food_risks, get_all_articles, find_similar_articles
from utils.scoring import compute_risk_score, score_to_label, get_top_drivers, get_supporting_articles
from services.json_loader import load_json
from services.embedding_service import embed_query

def get_evidence_for_food(
    food_id: str,
    active_signals: list[dict],
    signal_map: dict,
    articles_by_id: dict
) -> list[dict]:
    food_signal_types = {
        s["event_type"]
        for s in signal_map.get("mappings", {}).get(food_id, {}).get("signals", [])
    }
    evidence = []
    for signal in active_signals:
        if signal.get("event_type") not in food_signal_types:
            continue
        article_id = signal.get("article_id")
        article = articles_by_id.get(article_id, {})
        evidence.append({
            "event_type": signal.get("event_type"),
            "short_explanation": signal.get("short_explanation"),
            "source_title": article.get("title", ""),
            "source_name": article.get("source", ""),
            "source_date": article.get("published_at", ""),
            "source_url": article.get("url", "")
        })
    return evidence[:3]

def get_semantic_evidence(
    food_label: str,
    top_drivers: list[str]
) -> list[dict]:
    query = f"{food_label} supply chain disruption {' '.join(top_drivers[:2])}"
    query_embedding = embed_query(query)
    if not query_embedding:
        return []
    similar = find_similar_articles(query_embedding, top_k=3)
    return [
        {
            "title": a.get("title", ""),
            "source": a.get("source", ""),
            "published_at": a.get("published_at", ""),
            "relevance_score": round(a.get("score", 0), 3)
        }
        for a in similar
        if a.get("title")
    ]

def _compute_risks_from_signals(
    active_signals: list[dict],
    store: bool = True
) -> dict:
    weights = load_json("food_signal_weights.json")["weights"]
    signal_map = load_json("grocery_signal_map.json")
    groceries = load_json("groceries.json")["foods"]

    articles = get_all_articles()
    articles_by_id = {a["id"]: a for a in articles}

    risks = {}
    for food in groceries:
        food_id = food["id"]
        score = compute_risk_score(food_id, active_signals, weights)
        top_drivers = get_top_drivers(food_id, active_signals, weights)
        supporting_articles = get_supporting_articles(
            food_id, active_signals, signal_map
        )
        keyword_evidence = get_evidence_for_food(
            food_id, active_signals, signal_map, articles_by_id
        )
        semantic_evidence = get_semantic_evidence(food["label"], top_drivers)

        risk = {
            "food": food_id,
            "label": food["label"],
            "risk_score": score,
            "risk_label": score_to_label(score),
            "top_drivers": top_drivers,
            "supporting_articles": supporting_articles,
            "evidence": keyword_evidence,
            "semantic_evidence": semantic_evidence
        }

        if store:
            upsert_food_risk(risk)

        risks[food_id] = risk

    return risks

def compute_all_food_risks() -> dict:
    active_signals = get_all_signals()
    return _compute_risks_from_signals(active_signals, store=True)

def compute_food_risks_with_injected_signal(injected_signal: dict) -> dict:
    active_signals = get_all_signals()
    temp_signal = {
        **injected_signal,
        "article_id": "simulated",
        "extracted_at": "simulated"
    }
    augmented_signals = active_signals + [temp_signal]
    return _compute_risks_from_signals(augmented_signals, store=False)