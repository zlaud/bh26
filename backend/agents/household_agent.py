"""
Household Resilience Agent

This agent analyzes household grocery lists against current food supply chain risks
and provides personalized recommendations for building resilience.

The agent:
1. Receives HouseholdRequest with grocery list and household scale
2. Uses Gemini LLM with tools to assess risk for each food item
3. Identifies patterns and suggests substitutions for high-risk foods
4. Calculates collective impact of recommended actions
5. Returns comprehensive HouseholdResponse with strategies and evidence
"""

import os
import json
import asyncio
from uagents import Agent, Context, Model
import google.generativeai as genai
from dotenv import load_dotenv
from db.crud import get_all_food_risks, find_similar_articles
from services.json_loader import load_json
from services.embedding_service import embed_query

load_dotenv()
genai.configure(api_key=os.environ["GEMINI_API_KEY"])


class HouseholdRequest(Model):
    """
    Input message model for household grocery analysis requests.
    
    Attributes:
        groceries: Comma-separated list of food items (e.g., "eggs, bananas, milk")
        scale_id: Household scale identifier for impact calculations (e.g., "single", "family_4")
    """
    groceries: str
    scale_id: str


class HouseholdResponse(Model):
    """
    Output message model containing household resilience analysis.
    
    Attributes:
        result: JSON string with analysis results including risks, strategies, and impact
        success: Whether the analysis completed successfully
    """
    result: str
    success: bool

SYSTEM_PROMPT = """
You are the Household Resilience Agent for a food-system intelligence platform.
Help a household understand and adapt to current food-system disruptions.

Tools available:
1. get_food_risk(food_id) — get current live risk score and drivers for any food
2. get_substitutions(food_id) — get safe lower-risk alternatives for a food
3. find_similar_articles(query) — search MongoDB for supporting evidence

Steps:
1. Parse the grocery list
2. For each food call get_food_risk()
3. For HIGH risk foods call get_substitutions()
4. Call find_similar_articles() for evidence on top risks
5. Identify patterns across foods sharing the same signal
6. Return structured response

Rules:
- Explanation first, actions second
- Only recommend substitutes with lower current risk
- Classify each risk: emerging | active | sustained
- Tone: calm, practical, never alarming
- Do not invent foods, signals, or impacts

Return valid JSON only:
{
  "summary": "1-2 sentence overview",
  "top_risks": [{"food": "string", "risk_label": "LOW|MEDIUM|HIGH", "time_horizon": "emerging|active|sustained", "why": "string"}],
  "patterns": ["string"],
  "strategies": [{"type": "reduce_reliance|diversify|timing_adjustment|partial_substitution|flexible_consumption", "action": "string", "reason": "string"}],
  "recommendations": [{"food": "string", "action": "string", "why": "string", "estimated_monthly_savings": 0}],
  "evidence_panel": [{"food": "string", "drivers": ["string"], "headlines": ["string"]}],
  "collective_impact": {"scale_label": "string", "estimated_savings": 0, "co2_saved_kg": 0, "water_saved_liters": 0, "food_waste_reduced_kg": 0},
  "impact_explanation": {"summary": "string", "assumptions": ["string"]}
}
"""

TOOLS = [
    {
        "name": "get_food_risk",
        "description": "Get current live risk score, label, and top drivers for a food.",
        "parameters": {
            "type_": "OBJECT",
            "properties": {
                "food_id": {"type_": "STRING", "description": "Food ID e.g. eggs, bananas"}
            },
            "required": ["food_id"]
        }
    },
    {
        "name": "get_substitutions",
        "description": "Get safe lower-risk alternatives for a food.",
        "parameters": {
            "type_": "OBJECT",
            "properties": {
                "food_id": {"type_": "STRING", "description": "Food ID to find substitutes for"}
            },
            "required": ["food_id"]
        }
    },
    {
        "name": "find_similar_articles",
        "description": "Search MongoDB Vector Search for recent news relevant to a food supply query.",
        "parameters": {
            "type_": "OBJECT",
            "properties": {
                "query": {"type_": "STRING", "description": "Search query"}
            },
            "required": ["query"]
        }
    }
]

def get_food_risk_tool(food_id: str) -> dict:
    """
    Retrieve current risk assessment for a specific food item.
    
    This tool is called by the LLM to get live risk scores, labels (LOW/MEDIUM/HIGH),
    and top risk drivers for each food in the grocery list.
    
    Args:
        food_id: Food identifier (e.g., "eggs", "bananas")
        
    Returns:
        Dictionary with risk_score, risk_label, top_drivers, and supporting evidence
    """
    if not food_id or not food_id.strip():
        return {"error": "Food ID is required"}
    
    try:
        risks = get_all_food_risks()
        return risks.get(food_id, {"error": f"Food {food_id} not found"})
    except Exception as e:
        return {"error": f"Failed to get food risk: {str(e)}"}

def get_substitutions_tool(food_id: str) -> dict:
    """
    Get safe lower-risk alternative foods for substitution.
    
    This tool is called by the LLM when a food has HIGH risk to find
    suitable alternatives with lower current risk scores.
    
    Args:
        food_id: Food identifier to find substitutes for
        
    Returns:
        Dictionary with list of alternative foods and their properties
    """
    if not food_id or not food_id.strip():
        return {"error": "Food ID is required"}
    
    try:
        subs = load_json("substitutions.json")
        return subs.get("substitutions", {}).get(food_id, {"alternatives": []})
    except Exception as e:
        return {"error": f"Failed to get substitutions: {str(e)}"}

def find_similar_articles_tool(query: str) -> list[dict]:
    """
    Search MongoDB for recent news articles supporting risk assessments.
    
    This tool is called by the LLM to find evidence and context for
    the top risks affecting the household's grocery list.
    
    Args:
        query: Search query string from the LLM
        
    Returns:
        List of up to 3 relevant articles with titles, sources, and snippets
    """
    if not query or not query.strip():
        return []
    
    try:
        embedding = embed_query(query)
        if not embedding:
            return []
        return find_similar_articles(embedding, top_k=3)
    except Exception as e:
        print(f"Article search failed: {e}")
        return []

def run_household_agent(groceries: str, scale_id: str) -> dict | None:
    if not groceries or not groceries.strip():
        return {"error": "Groceries list is required"}
    if not scale_id or not scale_id.strip():
        return {"error": "Scale ID is required"}
    
    try:
        impact_assumptions = load_json("impact_assumptions.json")
    except Exception as e:
        print(f"Failed to load impact assumptions: {e}")
        impact_assumptions = {}

    model = genai.GenerativeModel(
        model_name="models/gemini-2.5-flash",
        system_instruction=SYSTEM_PROMPT,
        tools=TOOLS
    )
    chat = model.start_chat()
    
    user_message = f"""Grocery list: {groceries}
                    Scale ID: {scale_id}
                    Impact assumptions: {json.dumps(impact_assumptions, indent=2)}

                    Analyze this basket using your tools. Return valid JSON only."""

    response = chat.send_message(user_message)

    # Allow up to 6 rounds of tool calling for comprehensive analysis
    # LLM needs multiple rounds to check each food, find substitutions, and gather evidence
    for _ in range(6):
        if not response.candidates or not response.candidates[0].content.parts:
            return None
        
        tool_calls = [
            part for part in response.candidates[0].content.parts
            if hasattr(part, "function_call") and part.function_call.name
        ]
        
        if not tool_calls:
            break

        tool_results = []
        for part in tool_calls:
            fn = part.function_call
            
            try:
                # Route to appropriate tool function
                if fn.name == "get_food_risk":
                    result = get_food_risk_tool(fn.args.get("food_id", ""))
                elif fn.name == "get_substitutions":
                    result = get_substitutions_tool(fn.args.get("food_id", ""))
                elif fn.name == "find_similar_articles":
                    result = find_similar_articles_tool(fn.args.get("query", ""))
                else:
                    result = {"error": "Unknown tool"}
            except Exception as e:
                result = {"error": f"Tool execution failed: {str(e)}"}
            
            tool_results.append({
                "function_response": {
                    "name": fn.name,
                    "response": {"result": result}
                }
            })
        
        response = chat.send_message(tool_results)

    # Extract and parse JSON from LLM's final response
    if not response.candidates or not response.candidates[0].content.parts:
        return None
    
    for part in response.candidates[0].content.parts:
        if hasattr(part, "text") and part.text:
            try:
                clean = part.text.strip().replace("```json", "").replace("```", "").strip()
                return json.loads(clean)
            except json.JSONDecodeError:
                continue
    
    return None

household_agent = Agent(
    name="household_resilience_agent",
    seed=os.getenv("HOUSEHOLD_AGENT_SEED", "household_resilience_agent_seed_phrase"),
    port=8002,
    endpoint=["http://localhost:8002/submit"]
)

@household_agent.on_message(model=HouseholdRequest)
async def handle_household(ctx: Context, sender: str, msg: HouseholdRequest):
    ctx.logger.info(f"Analyzing basket: {msg.groceries[:50]}")
    
    try:
        # Run blocking LLM call in thread pool to avoid blocking event loop
        result = await asyncio.to_thread(run_household_agent, msg.groceries, msg.scale_id)
        await ctx.send(sender, HouseholdResponse(
            result=json.dumps(result) if result else json.dumps({"error": "Agent failed"}),
            success=result is not None
        ))
    except Exception as e:
        ctx.logger.error(f"Household agent failed: {e}")
        await ctx.send(sender, HouseholdResponse(
            result=json.dumps({"error": str(e)}),
            success=False
        ))

if __name__ == "__main__":
    household_agent.run()