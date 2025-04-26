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
    try:
        # Sanitize the input
        sanitized_input = raw_input.replace('\n', ' ').replace('\r', ' ')
        
        # Parse the input
        try:
            data = json.loads(sanitized_input)
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON input to generate_posts: {str(e)}")
            # Try to create a simplified version of the input
            data = {
                "strategy": "Create engaging content",
                "company_context": {"tone_of_voice": "Professional"},
                "brand_hero": "Brand mascot"
            }
        
        logger.info(f"Generating posts for strategy")
        
        # Create an agent to generate the posts
        agent = Agent(
            name="PostProposerTool",
            instructions=(
                "You are PostProposerTool.\n"
                "INPUT: A JSON object with strategy, company_context, and brand_hero.\n\n"
                "TASK: Create 3 engaging social media posts based on the strategy.\n\n"
                "Each post must include:\n"
                "- content: An engaging caption (max 120 chars)\n"
                "- hashtags: 2-3 relevant hashtags (short tags only)\n"
                "- call_to_action: A brief (under 20 chars) prompting phrase\n\n"
                "IMPORTANT: Your response MUST be a valid JSON array of post objects and nothing else."
            )
        )
        
        # Run the agent with sanitized input
        result = await Runner.run(agent, json.dumps(data))
        output = result.final_output
        
        # Try to parse the JSON output, with sanitization
        try:
            # Replace any non-printable characters
            clean_output = ''.join(char for char in output if char.isprintable() or char in ['\n', '\t', ' '])
            posts = json.loads(clean_output)
            
            if not isinstance(posts, list):
                logger.warning(f"Expected list but got {type(posts)}")
                posts = []
            return posts
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from generate_posts: {str(e)}")
            
            # Try to extract JSON if it's embedded in text
            import re
            json_pattern = r'\[\s*\{.*\}\s*\]'
            match = re.search(json_pattern, output, re.DOTALL)
            if match:
                try:
                    clean_match = ''.join(char for char in match.group(0) if char.isprintable() or char in ['\n', '\t', ' '])
                    posts = json.loads(clean_match)
                    if isinstance(posts, list):
                        return posts
                except:
                    pass
            
            # If all else fails, create a basic post
            return [{
                "content": "Our latest updates bring innovative solutions to your challenges. Stay tuned for more!",
                "hashtags": ["#Innovation", "#Solutions"],
                "call_to_action": "Learn more!"
            }]
            
    except Exception as e:
        logger.exception(f"Error in generate_posts: {str(e)}")
        # Return a fallback post if everything fails
        return [{
            "content": "We're excited to share our latest updates with you soon!",
            "hashtags": ["#ComingSoon", "#StayTuned"],
            "call_to_action": "Check back soon!"
        }]