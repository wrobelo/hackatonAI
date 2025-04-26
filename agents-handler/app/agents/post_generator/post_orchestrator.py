import os
import json
import logging
from typing import List, Dict, Any
from pymongo import MongoClient
from app.agents.post_generator.image_agent import ImageAgent
from app.agents.post_generator.post_generator_agent import generate_posts
from agents import function_tool, Agent, Runner
from dotenv import load_dotenv
load_dotenv() 

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ----------------------
# MongoDB Setup
# ----------------------
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB", "social_media")
mongo_client = MongoClient(MONGODB_URI)
db = mongo_client[MONGODB_DB]


async def fetch_company_data(company_id: str) -> Dict[str, Any]:
    """
    Retrieve company strategy, context, and brand hero from MongoDB.
    """
    client = MongoClient(MONGODB_URI)
    db = client[MONGODB_DB]
    doc = db.companies.find_one({"company_id": company_id})
    if not doc:
        logger.error("Company '%s' not found in '%s.companies'", company_id, MONGODB_DB)
        raise ValueError(f"Company '{company_id}' not found")

    return {
        "strategy": doc.get("strategy", ""),
        "company_context": doc.get("company_context", {}),
        "brand_hero": doc.get("mascot_description", "")
    }

class PostOrchestratorAgent:
    """
    High-level orchestrator for generating social-media post drafts and images.
    """
    def __init__(self):
        # Agent for content generation using the generate_posts tool
        self.content_agent = Agent(
            name="ContentAgent",
            instructions=(
                "You are ContentAgent. On receiving input, you MUST call the 'generate_posts' tool with the exact JSON input. "
                "Do NOT generate drafts directly. After calling the tool, return exactly its output (a JSON array) with NO additional text."
            ),
            tools=[generate_posts]
        )

        # Agent responsible for image creation
        self.image_agent = ImageAgent()

    async def generate(self, company_id: str) -> List[Dict[str, Any]]:
        # 1) Fetch configuration from MongoDB
        logger.info("Fetching data for company_id=%s", company_id)
        data = await fetch_company_data(company_id)
        payload = json.dumps(data)

        # 2) Generate content drafts
        logger.info("Generating post drafts")
        result = await Runner.run(self.content_agent, payload)
        raw = result.final_output
        
        # Simple JSON parsing with basic fallback
        try:
            drafts = json.loads(raw)
        except json.JSONDecodeError:
            logger.error("Invalid JSON from content_agent: %s", raw)
            
            # Simple fallback: create a basic post
            drafts = [{
                "content": "Discover our latest innovations designed with you in mind!",
                "hashtags": ["#Innovation", "#Solutions", "#Quality"],
                "call_to_action": "Learn more today!"
            }]

        # Make sure drafts is a list
        if not isinstance(drafts, list):
            drafts = [drafts] if drafts else []

        # 3) Generate images for each draft
        proposals: List[Dict[str, Any]] = []
        for idx, draft in enumerate(drafts, start=1):
            # Ensure the draft is a dictionary and has content
            if not isinstance(draft, dict):
                continue
                
            content = draft.get("content", "")
            if not content:
                continue

            # Ensure other required fields
            if "hashtags" not in draft:
                draft["hashtags"] = ["#Innovation"]
            if "call_to_action" not in draft:
                draft["call_to_action"] = "Learn more"

            logger.info("[%d] Generating image for draft", idx)
            
            # Create context for image generation
            image_context = {
                "content": content,
                "company_data": data
            }
            
            try:
                img_output = await self.image_agent.run(json.dumps(image_context))
            except Exception as e:
                logger.error(f"Image generation failed: {str(e)}")
                img_output = {
                    "scene_description": f"A scene featuring {data.get('brand_hero', 'our product')}.",
                    "image_url": ""
                }

            proposals.append({
                **draft,
                "scene_description": img_output.get("scene_description", ""),
                "image_url": img_output.get("image_url", "")
            })

        logger.info("Generated %d proposals for company_id=%s", len(proposals), company_id)
        return proposals