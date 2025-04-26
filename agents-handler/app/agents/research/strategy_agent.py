# strategy_agent.py

import os
import json
import logging
from typing import Any, Dict, List
import httpx
from pymongo import MongoClient
from openai import OpenAI

# ——— Logging & Config ———
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")
MONGO_URI          = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGO_DB           = os.getenv("MONGODB_DB", "social_media")
OPENAI_API_KEY     = os.getenv("OPENAI_API_KEY", "")

mongo = MongoClient(MONGO_URI)[MONGO_DB]
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# ——— Core Functions ———

async def fetch_trends(context: str) -> List[str]:
    """Fetch trending topics using Perplexity API."""
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


async def fetch_news(context: str) -> List[Dict[str, str]]:
    """Fetch news headlines using Perplexity API."""
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


async def generate_strategy(data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate content strategy using OpenAI."""
    try:
        # Create prompt with clear JSON format instructions
        prompt = f"""
        Create a weekly social media content strategy based on:
        
        COMPANY CONTEXT: {json.dumps(data.get('company_context', {}))}
        PREVIOUS STRATEGY: {json.dumps(data.get('strategy_context', {}))}
        TRENDS: {json.dumps(data.get('trends', []))}
        NEWS: {json.dumps(data.get('news', []))}
        
        Your response must be ONLY valid JSON with this structure:
        {{
          "goals": ["goal1", "goal2"],
          "topics": ["topic1", "topic2"],
          "tone": "content tone",
          "target_audience": ["audience1", "audience2"],
          "post_count": 3,
          "content_types": ["type1", "type2"],
          "schedule": {{"Monday": 1, "Wednesday": 1, "Friday": 1}},
          "rationale": "strategy explanation"
        }}
        """
        
        # Call OpenAI
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",  # Using 3.5 for wider compatibility
            messages=[
                {"role": "system", "content": "You are a social media strategist. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # Parse response
        content = response.choices[0].message.content.strip()
        
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON object using regex
            import re
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            raise
            
    except Exception as e:
        logger.error(f"Strategy generation error: {str(e)}")
        
        # Return fallback strategy
        return {
            "goals": ["Increase brand awareness", "Drive engagement"],
            "topics": ["Product innovations", "Customer success stories"],
            "tone": "Professional yet approachable",
            "target_audience": ["Tech professionals", "Business decision-makers"],
            "post_count": 3,
            "content_types": ["Image posts", "Text posts"],
            "schedule": {"Monday": 1, "Wednesday": 1, "Friday": 1},
            "rationale": "Default strategy based on best practices."
        }


# ——— Strategy Agent Class ———

class StrategyAgent:
    def __init__(self):
        pass

    async def propose(self, company_id: str) -> Dict[str, Any]:
        """Generate a content strategy proposal for the company."""
        try:
            # Fetch company data
            doc = mongo.companies.find_one(
                {"company_id": company_id},
                {"company_context": 1, "strategy_profile": 1}
            )
            if not doc:
                raise ValueError(f"Company '{company_id}' not found")
            
            company_context = doc.get("company_context", {})
            existing = doc.get("strategy_profile", {})
            
            # Fetch trends and news
            logger.info(f"Fetching trends for company: {company_id}")
            trends = await fetch_trends(json.dumps(company_context))
            logger.info(f"Fetched {len(trends)} trends")
            
            logger.info(f"Fetching news for company: {company_id}")
            news = await fetch_news(json.dumps(company_context))
            logger.info(f"Fetched {len(news)} news items")
            
            # Generate strategy
            logger.info(f"Generating strategy for company: {company_id}")
            strategy = await generate_strategy({
                "strategy_context": existing,
                "company_context": company_context,
                "trends": trends,
                "news": news
            })
            logger.info("Strategy generation complete")
            
            return {
                "trends": trends,
                "news": news,
                "strategy": strategy
            }
            
        except Exception as e:
            logger.exception(f"Strategy proposal failed: {str(e)}")
            # Return fallback data
            return {
                "trends": ["Content marketing", "Social engagement"],
                "news": [{"title": "Industry trends", "url": ""}],
                "strategy": {
                    "goals": ["Increase brand awareness", "Drive engagement"],
                    "topics": ["Product innovations", "Customer success stories"],
                    "tone": "Professional yet approachable",
                    "target_audience": ["Tech professionals", "Business decision-makers"],
                    "post_count": 3,
                    "content_types": ["Image posts", "Text posts"],
                    "schedule": {"Monday": 1, "Wednesday": 1, "Friday": 1},
                    "rationale": "Fallback strategy due to error."
                }
            }

    async def save(self, company_id: str, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Save a strategy to MongoDB for the given company."""
        try:
            logger.info(f"Saving strategy for company_id: {company_id}")
            
            # Update MongoDB
            result = mongo.companies.update_one(
                {"company_id": company_id},
                {"$set": {"strategy_profile": strategy}},
                upsert=True
            )
            
            return {
                "success": True,
                "matched_count": result.matched_count,
                "modified_count": result.modified_count,
                "upserted_id": str(result.upserted_id) if result.upserted_id else None,
                "message": "Strategy saved successfully"
            }
            
        except Exception as e:
            logger.exception(f"Error saving strategy: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to save strategy"
            }