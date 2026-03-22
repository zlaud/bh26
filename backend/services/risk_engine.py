import json
from db.crud import get_all_signals, upsert_food_risk, get_all_food_risks, get_all_articles
from utils.scoring import compute_risk_score, score_to_label, get_top_drivers, get_supporting_articles
from services.json_loader import load_json

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

def compute_all_food_risks() -> dict:
    weights = load_json("food_signal_weights.json")["weights"]
    signal_map = load_json("grocery_signal_map.json")
    groceries = load_json("groceries.json")["foods"]
    active_signals = get_all_signals()

    articles = get_all_articles()
    articles_by_id = {a["id"]: a for a in articles}

    risks = {}
    for food in groceries:
        food_id = food["id"]
        score = compute_risk_score(food_id, active_signals, weights)
        top_drivers = get_top_drivers(food_id, active_signals, weights)
        supporting_articles = get_supporting_articles(food_id, active_signals, signal_map)
        evidence = get_evidence_for_food(food_id, active_signals, signal_map, articles_by_id)

        risk = {
            "food": food_id,
            "label": food["label"],
            "risk_score": score,
            "risk_label": score_to_label(score),
            "top_drivers": top_drivers,
            "supporting_articles": supporting_articles,
            "evidence": evidence
        }
        upsert_food_risk(risk)
        risks[food_id] = risk

    return risks