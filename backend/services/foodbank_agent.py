from agents.foodbank_agent import run_foodbank_agent as run_foodbank_agent_logic

def run_foodbank_agent(region: str = "national") -> dict | None:
    result = run_foodbank_agent_logic(region=region)
    if result is None:
        return {"error": "Foodbank agent failed to return valid response"}
    return result