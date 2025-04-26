import json
import logging
from typing import List, Dict
from agents import Agent, Runner, function_tool
from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger(__name__)

class Post(BaseModel):
    content: str = Field(..., max_length=150, description="Engaging caption")
    hashtags: List[str] = Field(..., max_items=5, description="Up to 5 hashtags")
    call_to_action: str = Field(..., description="Prompting phrase")

class PostsOutput(BaseModel):
    posts: List[Post]

@function_tool(
    strict_mode=False,
    name_override="generate_posts",
    description_override=(
        "Generate a JSON array of social-media post drafts based on "
        "strategy, company_context, and brand_hero."
    )
)


async def generate_posts(raw_input: str) -> List[Dict]:
    # 1) Ensure raw_input is valid JSON for the agent
    try:
        json.loads(raw_input)
        payload = raw_input
    except json.JSONDecodeError:
        logger.warning("Invalid JSON input, using minimal fallback payload")
        fallback = {
            "strategy": "Create engaging content",
            "company_context": {"tone_of_voice": "professional"},
            "brand_hero": "Brand mascot"
        }
        payload = json.dumps(fallback)

    # 2) Build the Agent with a strict prompt
    agent = Agent(
        name="PostProposerTool",
        instructions=(
            "You are PostProposerTool.\n"
            "INPUT: a single JSON object with keys: strategy, company_context, brand_hero.\n"
            "TASK: Create exactly 3 engaging social media posts.\n\n"
            "Each post object must have exactly these keys:\n"
            "  • content        – string, max 120 chars\n"
            "  • hashtags       – array of 2–3 hashtag strings (without #)\n"
            "  • call_to_action – string, max 20 chars\n\n"
            "If you cannot fulfill the request, return an empty array: []\n"
            "OUTPUT: **EXACTLY** a JSON array of post objects, with no extra text or markup."
        )
    )

    # 3) Invoke the agent
    result = await Runner.run(agent, payload)
    raw = result.final_output.strip()
    logger.debug("Raw content_agent output: %r", raw)

    # 4) Extract the JSON array from any surrounding text
    m = re.search(r'(\[.*\])', raw, re.DOTALL)
    json_text = m.group(1) if m else raw

    # 5) Try strict JSON parse
    try:
        posts = json.loads(json_text)
        if isinstance(posts, list):
            return posts
        logger.warning("Parsed JSON not a list, got %s", type(posts))
    except json.JSONDecodeError as e:
        logger.warning("json.loads failed: %s", e)

    # 6) Try Python literal_eval
    try:
        posts = ast.literal_eval(json_text)
        if isinstance(posts, list):
            return posts
        logger.warning("literal_eval did not yield a list, got %s", type(posts))
    except Exception as e:
        logger.error("ast.literal_eval failed: %s", e)

    # 7) Ultimate fallback: single stub post
    logger.error("generate_posts: all parsing attempts failed, returning stub")
    return [{
        "content": "Discover our latest innovations designed with you in mind!",
        "hashtags": ["Innovation", "Solutions", "Quality"],
        "call_to_action": "Learn more!"
    }]
