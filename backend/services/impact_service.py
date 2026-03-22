from services.json_loader import load_json

def compute_collective_impact(action_ids: list[str], scale_id: str) -> dict:
    assumptions = load_json("impact_assumptions.json")

    scale = next(
        (s for s in assumptions["scales"] if s["id"] == scale_id),
        None
    )
    if not scale:
        return {"error": f"Unknown scale_id: {scale_id}"}

    multiplier = scale["multiplier"]
    totals = {
        "monthly_savings_usd": 0.0,
        "co2_saved_kg": 0.0,
        "water_saved_liters": 0.0,
        "food_waste_reduced_kg": 0.0
    }

    matched_actions = []
    for action_id in action_ids:
        action = next(
            (a for a in assumptions["actions"] if a["id"] == action_id),
            None
        )
        if not action:
            continue
        matched_actions.append(action["label"])
        for key in totals:
            totals[key] += action["per_household"][key] * multiplier

    eq = assumptions["scaling"]["equivalences"]
    equivalences = {
        "cars_off_road": round(
            totals["co2_saved_kg"] / (eq["co2_kg_per_car_year"]["value"] / 12), 1
        ),
        "days_of_water_per_person": round(
            totals["water_saved_liters"] / eq["water_liters_per_person_day"]["value"], 1
        ),
        "households_zero_food_waste": round(
            totals["food_waste_reduced_kg"] / (eq["food_waste_kg_per_household_year"]["value"] / 12), 1
        )
    }

    return {
        "scale_label": scale["label"],
        "multiplier": multiplier,
        "actions_applied": matched_actions,
        "totals": {k: round(v, 2) for k, v in totals.items()},
        "equivalences": equivalences
    }