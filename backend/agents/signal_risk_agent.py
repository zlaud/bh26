"""
Signal Risk Agent

This agent processes news articles and extracts structured risk signals related to
food supply chain disruptions using LLM-based analysis with function calling.

The agent:
1. Receives ArticleMessage containing news article data
2. Uses Gemini LLM with tools to analyze the article
3. Extracts structured risk signals (event type, severity, region, etc.)
4. Validates and returns SignalResponse with the extracted data
"""

import os
import json
import asyncio
from uagents import Agent, Context, Model
import google.generativeai as genai
from dotenv import load_dotenv
from services.json_loader import load_json
from services.embedding_service import embed_query
from db.crud import find_similar_articles

# Load environment variables and configure Gemini API
load_dotenv()
genai.configure(api_key=os.environ["GEMINI_API_KEY"])


class ArticleMessage(Model):
    """
    Input message model for news articles to be analyzed.
    
    Attributes:
        article_id: Unique identifier for the article
        title: Article headline
        snippet: Article content excerpt (first 600 chars)
        source: Publication source name
        published_at: Publication timestamp
        event_type_hint: Suggested event category from query
    """
    article_id: str
    title: str
    snippet: str
    source: str
    published_at: str
    event_type_hint: str


class SignalResponse(Model):
    """
    Output message model containing extracted risk signal data.
    
    Attributes:
        article_id: Reference to source article
        event_type: Classified event category
        region: Geographic area affected
        severity: Impact magnitude (0.0-1.0)
        confidence: Extraction confidence (0.0-1.0)
        affected_supply_chain: Food category impacted
        short_explanation: One-sentence impact summary
        relevant: Whether article is food supply related
    """
    article_id: str
    event_type: str
    region: str
    severity: float
    confidence: float
    affected_supply_chain: str
    short_explanation: str
    relevant: bool

VALID_EVENT_TYPES = {
    "shipping_disruption", "weather_extreme", "crop_disease", "animal_disease",
    "fuel_cost_spike", "labor_shortage", "trade_policy", "production_constraint",
    "currency_pressure", "conflict_instability", "contamination_recall", "demand_surge"
}

SYSTEM_PROMPT = """
You are a food supply chain analyst with access to tools.
Extract a structured risk signal from the news article provided.

Tools available:
1. find_similar_articles(query) — search MongoDB for corroborating articles
   to calibrate your severity score. More corroborating articles = higher severity.
2. get_event_taxonomy() — validate your event_type against the controlled vocabulary.

Steps:
1. Read the article
2. Call get_event_taxonomy() to confirm valid event types
3. Call find_similar_articles() to calibrate severity
4. Return your structured signal

Valid event_type values:
shipping_disruption, weather_extreme, crop_disease, animal_disease,
fuel_cost_spike, labor_shortage, trade_policy, production_constraint,
currency_pressure, conflict_instability, contamination_recall, demand_surge

Return JSON only:
{
  "event_type": "one of the valid types",
  "region": "geographic region e.g. US West Coast",
  "severity": 0.0 to 1.0,
  "confidence": 0.0 to 1.0,
  "affected_supply_chain": "e.g. livestock, imported_produce, wheat",
  "short_explanation": "1 sentence on food supply impact",
  "relevant": true
}

If not food supply relevant return: {"relevant": false}
"""

TOOLS = [
    {
        "name": "find_similar_articles",
        "description": "Search MongoDB Vector Search for articles similar to a query to calibrate severity.",
        "parameters": {
            "type_": "OBJECT",
            "properties": {
                "query": {"type_": "STRING", "description": "Search query"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_event_taxonomy",
        "description": "Get the controlled vocabulary of valid event types.",
        "parameters": {
            "type_": "OBJECT",
            "properties": {}
        }
    }
]

def find_similar_articles_tool(query: str) -> list[dict]:
    if not query or not query.strip():
        return []
    
    # Generate embedding for the query
    embedding = embed_query(query)
    if not embedding:
        return []
    
    # Perform vector search in MongoDB
    return find_similar_articles(embedding, top_k=3)

def get_event_taxonomy_tool() -> dict:
    return load_json("event_taxonomy.json")

def run_signal_extraction(article: ArticleMessage) -> dict | None:
    model = genai.GenerativeModel(
        model_name="models/gemini-2.5-flash",
        system_instruction=SYSTEM_PROMPT,
        tools=TOOLS
    )
    
    chat = model.start_chat()
    
    user_message = f"""Article title: {article.title}
                        Source: {article.source}
                        Published: {article.published_at}
                        Event type hint: {article.event_type_hint}

                        Article text:
                        {article.snippet}
                    """

    response = chat.send_message(user_message)

    # Allow up to 3 rounds of tool calling
    # LLM can iteratively call tools to gather information before final response
    for _ in range(3):
        # Validate response structure
        if not response.candidates or not response.candidates[0].content.parts:
            return None
        
        # Extract any function calls from the response
        tool_calls = [
            part for part in response.candidates[0].content.parts
            if hasattr(part, "function_call") and part.function_call.name
        ]
        
        # If no tool calls, LLM is done and ready to return final answer
        if not tool_calls:
            break

        # Execute each tool call and collect results
        tool_results = []
        for part in tool_calls:
            fn = part.function_call
            try:
                # Route to appropriate tool function
                if fn.name == "find_similar_articles":
                    result = find_similar_articles_tool(fn.args.get("query", ""))
                elif fn.name == "get_event_taxonomy":
                    result = get_event_taxonomy_tool()
                else:
                    result = {"error": "Unknown tool"}
            except Exception as e:
                # Catch tool execution errors and return error message to LLM
                result = {"error": f"Tool execution failed: {str(e)}"}
            
            # Format tool result for LLM
            tool_results.append({
                "function_response": {
                    "name": fn.name,
                    "response": {"result": result}
                }
            })
        
        # Send tool results back to LLM for next turn
        response = chat.send_message(tool_results)

    # Validate final response structure
    if not response.candidates or not response.candidates[0].content.parts:
        return None

    # Extract and parse JSON from LLM's text response
    for part in response.candidates[0].content.parts:
        if hasattr(part, "text") and part.text:
            try:
                clean = part.text.strip().replace("```json", "").replace("```", "").strip()
                return json.loads(clean)
            except json.JSONDecodeError:
                continue
    
    # Return None if no valid JSON found
    return None

def validate_signal(data: dict) -> bool:
    if not data.get("relevant", True):
        return False
    required = ["event_type", "region", "severity", "confidence",
                "affected_supply_chain", "short_explanation"]
    if not all(k in data for k in required):
        return False
    if data["event_type"] not in VALID_EVENT_TYPES:
        return False
    
    # Validate numeric fields are in valid range
    try:
        if not (0.0 <= float(data["severity"]) <= 1.0):
            return False
        if not (0.0 <= float(data["confidence"]) <= 1.0):
            return False
    except (ValueError, TypeError):
        return False
    
    return True

# Initialize the uAgent with configuration
# The agent listens on port 8001 for incoming ArticleMessage messages
signal_risk_agent = Agent(
    name="signal_risk_agent",
    seed=os.getenv("SIGNAL_AGENT_SEED", "signal_risk_agent_seed_phrase"),
    port=8001,
    endpoint=["http://localhost:8001/submit"]
)

@signal_risk_agent.on_message(model=ArticleMessage)
async def handle_article(ctx: Context, sender: str, msg: ArticleMessage):
    ctx.logger.info(f"Processing: {(msg.title or '')[:60]}")
    
    try:
        # Run blocking LLM call in thread pool to avoid blocking event loop
        result = await asyncio.to_thread(run_signal_extraction, msg)
        
        # Validate and send successful extraction
        if result and validate_signal(result):
            await ctx.send(sender, SignalResponse(
                article_id=msg.article_id,
                event_type=result["event_type"],
                region=result["region"],
                severity=float(result["severity"]),
                confidence=float(result["confidence"]),
                affected_supply_chain=result["affected_supply_chain"],
                short_explanation=result["short_explanation"],
                relevant=True
            ))
        else:
            # Send empty response if extraction failed or article not relevant
            await ctx.send(sender, SignalResponse(
                article_id=msg.article_id,
                event_type="", region="",
                severity=0.0, confidence=0.0,
                affected_supply_chain="", short_explanation="",
                relevant=False
            ))
    except Exception as e:
        # Log error and send empty response to prevent deadlock
        ctx.logger.error(f"Signal extraction failed: {e}")
        await ctx.send(sender, SignalResponse(
            article_id=msg.article_id,
            event_type="", region="",
            severity=0.0, confidence=0.0,
            affected_supply_chain="", short_explanation="",
            relevant=False
        ))

if __name__ == "__main__":
    signal_risk_agent.run()