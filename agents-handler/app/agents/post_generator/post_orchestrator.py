import os
import json
import logging
from typing import List, Dict, Any, Optional
from pymongo import MongoClient
from app.agents.post_generator.image_agent import ImageAgent
from app.agents.post_generator.post_generator_agent import generate_posts
from app.company_context_agents.prompts import get_edit_agent_prompt
from agents import function_tool, Agent, Runner, ModelSettings
from dotenv import load_dotenv
from bson.json_util import dumps, loads
import bson
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
MONGODB_DB = os.getenv("MONGODB_DB", "brand-hero")
mongo_client = MongoClient(MONGODB_URI)
db = mongo_client[MONGODB_DB]
# Collections for storing post edit conversations and posts
post_edit_conversations = db["post_edit_conversations"]
posts_collection = db["posts"]


async def fetch_company_data(company_id: str) -> Dict[str, Any]:
    doc = db.company_context_memory.find_one({"company_id": company_id})
    if not doc:
        raise ValueError(f"Company '{company_id}' not found")

    # Convert the ObjectId into a string
    doc["_id"] = str(doc["_id"])
    return doc

@function_tool
async def update_post_content(post_data: str, updated_content: str) -> Dict[str, Any]:
    post = json.loads(post_data)
    post["content"] = updated_content
    return post

@function_tool
async def update_post_image(post_data: str, scene_description: str, company_id: str) -> Dict[str, Any]:
    post = json.loads(post_data)
    company_data = await fetch_company_data(company_id)
    image_agent = ImageAgent()
    context = {"content": post.get("content",""), "scene_description": scene_description, "company_data": company_data}
    img_out = await image_agent.run(json.dumps(context))
    post.update({"scene_description": scene_description, "image_url": img_out.get("image_url",""), "company_id": company_id})
    return post

@function_tool
async def update_post_hashtags(post_data: str, hashtags: List[str]) -> Dict[str, Any]:
    post = json.loads(post_data)
    post["hashtags"] = hashtags
    return post

@function_tool
async def update_post_cta(post_data: str, call_to_action: str) -> Dict[str, Any]:
    post = json.loads(post_data)
    post["call_to_action"] = call_to_action
    return post

@function_tool
async def update_full_post(
    post_data: str,
    content: str,
    hashtags: List[str],
    call_to_action: str,
    scene_description: str,
    company_id: str
) -> Dict[str, Any]:
    post = json.loads(post_data)
    company_data = await fetch_company_data(company_id)
    image_agent = ImageAgent()
    context = {"content": content, "scene_description": scene_description, "company_data": company_data}
    img_out = await image_agent.run(json.dumps(context))
    post.update({
        "content": content,
        "hashtags": hashtags,
        "call_to_action": call_to_action,
        "scene_description": scene_description,
        "image_url": img_out.get("image_url",""),
        "company_id": company_id
    })
    return post

@function_tool
async def save_post(post_data: str) -> Dict[str, Any]:
    post = json.loads(post_data)
    if "post_id" not in post:
        post["post_id"] = str(bson.ObjectId())
    if "company_id" not in post:
        raise ValueError("company_id is required to save a post")
    posts_collection.update_one({"post_id": post["post_id"]}, {"$set": post}, upsert=True)
    logger.info(f"Saved post_id={post['post_id']}")
    return {"success": True, "post": post}


async def dynamic_instructions(wrapper, agent) -> str:
    cid = wrapper.context['company_id']
    return get_edit_agent_prompt(cid)


class PostOrchestratorAgent:
    def __init__(self):
        self.content_agent = Agent(
            name="ContentAgent",
            instructions=(
                "You are ContentAgent. On receiving input, you MUST call the 'generate_posts' tool with the exact JSON input. "
                "Do NOT generate drafts directly. Return exactly its JSON output."
            ),
            tools=[generate_posts]
        )
        self.image_agent = ImageAgent()
        self.edit_agent = Agent(
            name="PostEditAgent",
            instructions=dynamic_instructions,
            tools=[update_post_content, update_post_image, update_post_hashtags, update_post_cta, update_full_post, save_post],
            model="gpt-3.5-turbo",
            model_settings=ModelSettings(tool_choice="auto")
        )

    async def generate(self, company_id: str, save_to_db: bool = False) -> List[Dict[str, Any]]:
        data = await fetch_company_data(company_id)
        result = await Runner.run(self.content_agent, json.dumps(data))
        try:
            drafts = json.loads(result.final_output.strip())
        except json.JSONDecodeError:
            logger.error("Invalid JSON from ContentAgent: %s", result.final_output)
            drafts = []
        proposals = []
        for draft in (drafts if isinstance(drafts, list) else [drafts]):
            if not draft.get("content"): continue
            draft.setdefault("hashtags", ["#Innovation"])
            draft.setdefault("call_to_action", "Learn more")
            img_context = {"content": draft["content"], "company_data": data}
            try:
                img_out = await self.image_agent.run(json.dumps(img_context))
            except Exception:
                img_out = {"scene_description": "", "image_url": ""}
            post = {
                "post_id": str(bson.ObjectId()),
                "company_id": company_id,
                "content": draft["content"],
                "hashtags": draft["hashtags"],
                "call_to_action": draft["call_to_action"],
                "scene_description": img_out.get("scene_description",""),
                "image_url": img_out.get("image_url","")
            }
            if save_to_db:
                posts_collection.update_one({"post_id": post["post_id"]}, {"$set": post}, upsert=True)
            proposals.append(post)
        return proposals

    async def edit_post(
        self,
        post_data: Dict[str, Any],
        company_id: str,
        user_response: Optional[str] = None
    ) -> Dict[str, Any]:
        # Ensure full original post is in context
        conversation_id = post_data.get("conversation_id", str(bson.ObjectId()))
        post_data["company_id"] = company_id
        context = {"post_data": json.dumps(post_data), "company_id": company_id, "conversation_id": conversation_id}

        # Load previous conversation state
        doc = post_edit_conversations.find_one({"conversation_id": conversation_id})
        prev_id = doc.get("previous_response_id") if doc else None

        # Run the editing agent
        if prev_id and user_response:
            result = await Runner.run(
                self.edit_agent,
                context=context,
                previous_response_id=prev_id,
                input=user_response
            )
        else:
            result = await Runner.run(
                self.edit_agent,
                context=context,
                input=""
            )

        last_id = getattr(result, 'last_response_id', None)
        # Persist conversation state
        post_edit_conversations.update_one(
            {"conversation_id": conversation_id},
            {"$set": {"previous_response_id": last_id, "company_id": company_id, "post_data": post_data}},
            upsert=True
        )

        raw = result.final_output or ""
        # Attempt to parse JSON generated by the agent
        try:
            output_json = json.loads(raw)
        except json.JSONDecodeError:
            output_json = None

        # Determine final post state
        if output_json and all(k in output_json for k in [
            "post_id", "company_id", "content", "hashtags",
            "call_to_action", "scene_description", "image_url"
        ]):
            # Agent has returned a complete post structure; save and return it
            try:
                saved = await save_post(json.dumps(output_json))
                final_post = saved.get("post", output_json)
            except Exception as e:
                logger.error("Error saving post: %s", e)
                final_post = output_json
        else:
            # No full post JSON; return current post_data as draft
            final_post = post_data

        return {
            "conversation_id": conversation_id,
            "company_id": company_id,
            "post": final_post,
            "response_id": last_id
        }
