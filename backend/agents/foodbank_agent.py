"""
Food Bank Operations Agent

This agent generates forward-looking operational guidance for food banks based on
current food supply chain risks and trajectory analysis.

The agent:
1. Receives FoodbankRequest with region specification
2. Uses Gemini LLM with tools to assess risks and load operational playbook
3. Analyzes risk trajectories (emerging, active, sustained)
4. Generates procurement and substitution recommendations
5. Returns FoodbankResponse with prioritized operational actions
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


class FoodbankRequest(Model):
    """
    Input message model for food bank operational analysis requests.
    
    Attributes:
        region: Geographic region for analysis (default: "national")
    """
    region: str = "national"


class FoodbankResponse(Model):
    """
    Output message model containing food bank operational guidance.
    
    Attributes:
        result: JSON string with analysis including risks, trajectories, and actions
        success: Whether the analysis completed successfully
    """
    result: str
    success: bool

SYSTEM_PROMPT = """
You are the Food Bank Operations Agent for a food system resilience platform.
Think in two layers: current state and trajectory.

Tools available:
1. get_food_risk(food_id) — get current live risk score and drivers
2. get_foodbank_rules() — get the operational playbook
3. find_similar_articles(query) — search MongoDB for trajectory evidence

Steps:
1. Call get_foodbank_rules() to load the playbook
2. For each high-risk food category call get_food_risk()
3. Call find_similar_articles() for trajectory evidence on top risks
4. Return forward-looking operational guidance

Anticipation rules:
- Always frame risks as trajectories, never static facts
- NOT: "eggs are expensive"
- YES: "egg prices are likely to climb further as avian flu pressure builds"
- Classify: emerging | active | sustained
- Order: CRITICAL first → immediate → watch
- Reference procurement_notes from rules when justifying substitutions

Return valid JSON only:
{
  "summary": "2-3 sentences: current conditions, trajectory, most important action window",
  "top_risks": [{"food": "string", "risk_label": "LOW|MEDIUM|HIGH|CRITICAL", "current_state": "string", "time_horizon": "emerging|active|sustained", "trajectory": "string"}],
  "patterns": ["string"],
  "procurement_actions": [{"priority": 1, "urgency": "critical|immediate|watch", "action": "string", "reason": "string"}],
  "substitution_actions": [{"from": "string", "to": "string", "urgency": "critical|immediate|watch", "action": "string", "reason": "string"}]
}
"""

TOOLS = [
    {
        "name": "get_food_risk",
        "description": "Get current live risk score, label, and top drivers for a food.",
        "parameters": {
            "type_": "OBJECT",
            "properties": {
                "food_id": {"type_": "STRING", "description": "Food ID e.g. eggs, chicken"}
            },
            "required": ["food_id"]
        }
    },
    {
        "name": "get_foodbank_rules",
        "description": "Get the food bank operational playbook with procurement rules and substitution categories.",
        "parameters": {
            "type_": "OBJECT",
            "properties": {}
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
    
    This tool is called by the LLM to get live risk scores, labels,
    and top risk drivers for food bank procurement planning.
    
    Args:
        food_id: Food identifier (e.g., "eggs", "chicken")
        
    Returns:
        Dictionary with risk_score, risk_label, top_drivers, and evidence
    """
    if not food_id or not food_id.strip():
        return {"error": "Food ID is required"}
    
    try:
        risks = get_all_food_risks()
        return risks.get(food_id, {"error": f"Food {food_id} not found"})
    except Exception as e:
        return {"error": f"Failed to get food risk: {str(e)}"}

def get_foodbank_rules_tool() -> dict:
    """
    Load the food bank operational playbook.
    
    This tool is called by the LLM to access procurement rules,
    substitution categories, and operational guidelines.
    
    Returns:
        Dictionary with food bank operational rules and playbook
    """
    try:
        return load_json("foodbank_rules.json")
    except Exception as e:
        return {"error": f"Failed to load foodbank rules: {str(e)}"}

def find_similar_articles_tool(query: str) -> list[dict]:
    """
    Search MongoDB for recent news articles for trajectory analysis.
    
    This tool is called by the LLM to find evidence about risk trajectories
    (emerging, active, sustained) to inform forward-looking guidance.
    
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

def run_foodbank_agent(region: str = "national") -> dict | None:
    model = genai.GenerativeModel(
        model_name="models/gemini-2.5-flash",
        system_instruction=SYSTEM_PROMPT,
        tools=TOOLS
    )
    chat = model.start_chat()
    
    user_message = f"""Generate this week's food bank operations briefing for region: {region}.
                        Use your tools to get current risk data and the operational playbook.
                        Return valid JSON only."""

    response = chat.send_message(user_message)

    # Allow up to 8 rounds of tool calling for comprehensive analysis
    # LLM needs multiple rounds to check multiple foods and gather trajectory evidence
    for _ in range(8):
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
                elif fn.name == "get_foodbank_rules":
                    result = get_foodbank_rules_tool()
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

foodbank_agent = Agent(
    name="foodbank_operations_agent",
    seed=os.getenv("FOODBANK_AGENT_SEED", "foodbank_operations_agent_seed_phrase"),
    port=8003,
    endpoint=["http://localhost:8003/submit"]
)

@foodbank_agent.on_message(model=FoodbankRequest)
async def handle_foodbank(ctx: Context, sender: str, msg: FoodbankRequest):
    ctx.logger.info(f"Running foodbank analysis for: {msg.region}")
    
    try:
        # Run blocking LLM call in thread pool to avoid blocking event loop
        result = await asyncio.to_thread(run_foodbank_agent, msg.region)
        await ctx.send(sender, FoodbankResponse(
            result=json.dumps(result) if result else json.dumps({"error": "Agent failed"}),
            success=result is not None
        ))
    except Exception as e:
        ctx.logger.error(f"Foodbank agent failed: {e}")
        await ctx.send(sender, FoodbankResponse(
            result=json.dumps({"error": str(e)}),
            success=False
        ))

if __name__ == "__main__":
    foodbank_agent.run()