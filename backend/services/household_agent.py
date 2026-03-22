import json
from db.crud import get_all_food_risks
from agents.household_agent import run_household_agent as run_household_agent_logic
from services.json_loader import load_json

def normalize_grocery_list(raw: str) -> list[str]:
    groceries = load_json("groceries.json")
    valid_ids = {food["id"] for food in groceries["foods"]}
    label_to_id = {
        food["label"].lower(): food["id"]
        for food in groceries["foods"]
    }
    items = [item.strip().lower() for item in raw.split(",") if item.strip()]
    normalized = []
    for item in items:
        if item in valid_ids:
            normalized.append(item)
        elif item in label_to_id:
            normalized.append(label_to_id[item])
    return list(dict.fromkeys(normalized))

def run_household_agent(
    raw_grocery_input: str,
    scale_id: str = "100_households"
) -> dict | None:
    user_foods = normalize_grocery_list(raw_grocery_input)
    if not user_foods:
        return {"error": "No recognized foods in grocery list"}

    groceries_str = ",".join(user_foods)
    result = run_household_agent_logic(groceries_str, scale_id)

    if result:
        food_risks = get_all_food_risks()
        result["user_foods"] = user_foods
        result["food_risks"] = {
            f: food_risks[f]
            for f in user_foods
            if f in food_risks
        }

    return result