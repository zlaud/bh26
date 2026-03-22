def compute_risk_score(
    food_id: str,
    active_signals: list[dict],
    weights: dict
) -> float:
    food_weights = weights.get(food_id, {})

    # group signals by event_type
    # for each event_type take only the strongest signal
    best_by_type: dict[str, float] = {}

    for signal in active_signals:
        event_type = signal.get("event_type")
        if event_type not in food_weights:
            continue
        weight = food_weights[event_type]
        severity = signal.get("severity", 0.5)
        confidence = signal.get("confidence", 0.5)
        contribution = weight * severity * confidence

        if event_type not in best_by_type or contribution > best_by_type[event_type]:
            best_by_type[event_type] = contribution

    if not best_by_type:
        return 0.0

    # sort contributions descending
    contributions = sorted(best_by_type.values(), reverse=True)

    # primary signal carries full weight
    # each additional signal adds diminishing returns
    score = contributions[0]
    for i, c in enumerate(contributions[1:], start=2):
        score += c / (i * 4)

    return round(min(score, 1.0), 3)

def score_to_label(score: float) -> str:
    if score >= 0.75:
        return "HIGH"
    elif score >= 0.50:
        return "MEDIUM"
    return "LOW"

def get_top_drivers(food_id: str, active_signals: list[dict], weights: dict, top_n: int = 3) -> list[str]:
    food_weights = weights.get(food_id, {})
    scored = []
    for signal in active_signals:
        event_type = signal.get("event_type")
        if event_type not in food_weights:
            continue
        contribution = food_weights[event_type] * signal.get("severity", 0.5) * signal.get("confidence", 0.5)
        scored.append((event_type, contribution))
    scored.sort(key=lambda x: x[1], reverse=True)
    return [e for e, _ in scored[:top_n]]

def get_supporting_articles(food_id: str, active_signals: list[dict], signal_map: dict) -> list[str]:
    food_signal_types = {
        s["event_type"]
        for s in signal_map.get("mappings", {}).get(food_id, {}).get("signals", [])
    }
    article_ids = []
    for signal in active_signals:
        if signal.get("event_type") in food_signal_types:
            article_id = signal.get("article_id")
            if article_id:
                article_ids.append(article_id)
    return list(set(article_ids))