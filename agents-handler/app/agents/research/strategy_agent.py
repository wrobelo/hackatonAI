# strategy_agent.py

import os
import json
import logging
from typing import Any, Dict, List, Optional
import httpx
from pymongo import MongoClient
from agents import Agent, Runner, function_tool, ModelSettings
from openai import OpenAI
from app.company_context_agents.prompts import get_strategy_agent_prompt
# ——— Logging & Config ———
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
MONGO_URI          = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGO_DB           = os.getenv("MONGODB_DB", "brand-hero")
OPENAI_API_KEY     = os.getenv("OPENAI_API_KEY", "")

mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client[MONGO_DB]
# Conversation memory collection
strategy_conversations = mongo_db["strategy_conversations"]
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# ——— Function Tools ———

@function_tool
async def fetch_trends(company_id: str) -> List[str]:
    """
    Fetch trending topics using Perplexity API based on company context.
    Returns a list of trending topics.
    """
    logger.info(f"Fetching trends for company_id: {company_id}")
    # Get company context
    doc = mongo_db.company_context_memory.find_one(
        {"company_id": company_id},
        {"company_context": 1}
    )
    if not doc:
        logger.warning(f"Company '{company_id}' not found")
        return ["Content marketing", "Social engagement", "Video content"]
    
    context = json.dumps(doc.get("company_context", {}))
    prompt = f"List the top 10 social media trends related to: {context}\nFormat as a numbered list."
    
    try:
        # Call Perplexity API
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "sonar",
                    "messages": [
                        {"role": "system", "content": "Be concise."},
                        {"role": "user", "content": prompt}
                    ]
                }
            )
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
        
        # Parse numbered list
        import re
        trends = re.findall(r'\d+\.\s*(.+)', content)
        
        # Fallback to line splitting if regex didn't work
        if not trends:
            trends = [line.strip() for line in content.splitlines() if line.strip()]
            
        # Return trends (max 10)
        return trends[:10] if trends else ["Content marketing", "Social engagement", "Video content"]
        
    except Exception as e:
        logger.error(f"Error fetching trends: {str(e)}")
        return ["Content marketing", "Social engagement", "Video content"]


@function_tool
async def fetch_news(company_id: str) -> List[Dict[str, str]]:
    """
    Fetch news headlines using Perplexity API based on company context.
    Returns a list of news items.
    """
    # Get company context
    doc = mongo_db.company_context_memory.find_one(
        {"company_id": company_id},
        {"company_context": 1}
    )
    if not doc:
        logger.warning(f"Company '{company_id}' not found")
        return [{"title": "Industry trends", "url": ""}]
    
    context = json.dumps(doc.get("company_context", {}))
    prompt = f"Provide 5 recent news headlines related to: {context}\nFormat as a numbered list."
    
    try:
        # Call Perplexity API
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "sonar",
                    "messages": [
                        {"role": "system", "content": "Be concise."},
                        {"role": "user", "content": prompt}
                    ]
                }
            )
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
        
        # Parse numbered list
        import re
        headlines = re.findall(r'\d+\.\s*(.+)', content)
        
        # Fallback to line splitting if regex didn't work
        if not headlines:
            headlines = [line.strip() for line in content.splitlines() if line.strip()]
            
        # Convert to dictionaries
        news = [{"title": headline, "url": ""} for headline in headlines[:5]]
        return news if news else [{"title": "Industry trends", "url": ""}]
        
    except Exception as e:
        logger.error(f"Error fetching news: {str(e)}")
        return [{"title": "Industry trends", "url": ""}]


@function_tool
async def generate_strategy_proposal(company_id: str, trends: List[str], news: List[str]) -> str:
    """
    Generate a social media content strategy proposal using OpenAI.
    Returns serialized JSON string of the strategy.
    """
    try:
        # Get company context
        doc = mongo_db.company_context_memory.find_one(
            {"company_id": company_id},
            {"company_context": 1, "strategy_profile": 1}
        )
        company_context = doc.get("company_context", {}) if doc else {}
        existing_strategy = doc.get("strategy_profile", {}) if doc else {}
        
        # Create prompt with clear JSON format instructions
        prompt = f"""
        Create a weekly social media content strategy based on:
        
        COMPANY CONTEXT: {json.dumps(company_context)}
        PREVIOUS STRATEGY: {json.dumps(existing_strategy)}
        TRENDS: {json.dumps(trends)}
        NEWS: {json.dumps(news)}
        
        Your response must be ONLY valid JSON with goals, topics, tone, etc.
        """
        
        # Call OpenAI
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a social media strategist. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # Parse and re-serialize to ensure valid JSON
        content = response.choices[0].message.content.strip()
        try:
            parsed = json.loads(content)
            return json.dumps(parsed)
        except json.JSONDecodeError:
            import re
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                return match.group(0)
            raise
            
    except Exception as e:
        logger.error(f"Strategy generation error: {str(e)}")
        
        # Return fallback strategy
        fallback = {
            "goals": ["Increase brand awareness", "Drive engagement"],
            "topics": ["Product innovations", "Customer success stories"],
            "tone": "Professional yet approachable",
            "target_audience": ["Tech professionals", "Business decision-makers"],
            "post_count": 3,
            "content_types": ["Image posts", "Text posts"],
            "schedule": {"Monday": 1, "Wednesday": 1, "Friday": 1},
            "rationale": "Default strategy based on best practices."
        }
        return json.dumps(fallback)


@function_tool
async def save_strategy(company_id: str, strategy_json: str) -> str:
    """
    Save a strategy to MongoDB for the given company.
    Takes strategy as JSON string and returns result as JSON string.
    """
    try:
        logger.info(f"Saving strategy for company_id: {company_id}")
        
        # Parse the strategy from JSON
        strategy = json.loads(strategy_json)
        
        # Update MongoDB
        result = mongo_db.strategies.update_one(
            {"company_id": company_id},
            {"$set": {"strategy": strategy}},
            upsert=True
        )
        
        return json.dumps({
            "success": True,
            "matched_count": result.matched_count,
            "modified_count": result.modified_count,
            "upserted_id": str(result.upserted_id) if result.upserted_id else None,
            "message": "Strategy saved successfully"
        })
        
    except Exception as e:
        logger.exception(f"Error saving strategy: {str(e)}")
        return json.dumps({
            "success": False,
            "error": str(e),
            "message": "Failed to save strategy"
        })

async def dynamic_instructions(wrapper, agent) -> str:
    cid = wrapper.context['company_id']
    return get_strategy_agent_prompt(cid)


# ——— Strategy Agent Class ———
class StrategyAgent:
    def __init__(self):
        logger.info("Initializing StrategyAgent")
        self.agent = Agent(
            name="SocialMediaStrategy",
            instructions=dynamic_instructions,
            model="o4-mini",
            tools=[fetch_trends, fetch_news, generate_strategy_proposal, save_strategy],
            model_settings=ModelSettings(tool_choice="auto")
        )

    async def run(self, company_id: str, user_response: Optional[str] = None) -> Dict[str, Any]:
        # Always use the passed company_id from the request
        context = {"company_id": company_id}
        logger.info(f"Runninng strategy agent for context={context}")

        # Retrieve any previous conversation state
        doc = strategy_conversations.find_one({"company_id": company_id})
        prev_id = doc.get("previous_response_id") if doc else None

        # Determine whether to continue or start fresh
        if user_response and prev_id:
            logger.info(f"Continuing strategy conversation for company_id={company_id}")
            result = await Runner.run(
                self.agent,
                context=context,
                previous_response_id=prev_id,
                input=user_response
            )
        else:
            logger.info(f"Starting initial strategy for company_id={company_id}")
            result = await Runner.run(
                self.agent,
                context=context,
                input=""
            )

        # Extract new conversation ID for persistence
        last_id = getattr(result, 'last_response_id', None)
        if last_id:
            strategy_conversations.update_one(
                {"company_id": company_id},
                {"$set": {"previous_response_id": last_id}},
                upsert=True
            )
            logger.info(f"Updated previous_response_id for company_id={company_id}")

        # Always return the original company_id
        return {
            "company_id": company_id,
            "output": getattr(result, 'final_output', None),
            "conversation_id": last_id
        }

# Expose agent and runner for api.py
agent_instance = StrategyAgent()
agent = agent_instance.agent
runner = Runner()

async def run_strategy_agent(agent, company_id, user_response=None):
    return await agent_instance.run(company_id, user_response)

async def get_strategy_by_company_id(company_id: str):
    """
    Get the strategy for a specific company by company_id.
    Returns the strategy from MongoDB.
    """
    try:
        # Query MongoDB for the strategy
        strategy_doc = mongo_db.strategies.find_one({"company_id": company_id})
        
        if not strategy_doc:
            return {"error": f"No strategy found for company_id: {company_id}"}, 404
        
        # Return the strategy
        return {
            "company_id": company_id,
            "strategy": strategy_doc.get("strategy", {})
        }, 200
    except Exception as e:
        return {"error": f"Error fetching strategy: {str(e)}"}, 500
