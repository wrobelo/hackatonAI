import json
import logging
import os
from openai import OpenAI
from typing import Dict
from agents import Agent, Runner, function_tool
from dotenv import load_dotenv
load_dotenv() 

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
logger = logging.getLogger(__name__)

@function_tool(
    strict_mode=False,
    name_override='generate_image',
    description_override='Generate a high-quality image with DALL·E using the scene description.'
)
async def generate_image(prompt: str) -> Dict[str, str]:
    try:
        logger.info(f"Generating image with prompt: {prompt[:50]}...")
        img_resp = client.images.generate(prompt=prompt,
        n=1,
        size="1024x1024")
        url = img_resp.data[0].url
        logger.info(f"Successfully generated image URL: {url[:30]}...")
        return {"image_url": url}
    except Exception as e:
        logger.error(f"Image generation failed: {str(e)}")
        return {"image_url": "", "error": str(e)}
    

@function_tool(
    strict_mode=False,
    name_override='scene_description',
    description_override='Create a concise scene description for the image, incorporating the brand hero.'
)
async def scene_description(context_json: str) -> Dict[str, str]:
    # Parse the enriched context that includes both post content and company data
    try:
        context = json.loads(context_json)
        content = context.get("content", "")
        company_data = context.get("company_data", {})
        brand_hero = company_data.get("brand_hero", "")
        
        # Create an enriched prompt for the scene description
        enriched_prompt = (
            f"Post content: {content}\n"
            f"Company context: {company_data.get('company_context', {})}\n"
            f"Brand hero/mascot: {brand_hero}\n"
            f"Create a vivid scene description incorporating the brand hero."
        )
        
        logger.info(f"Generating scene description with enriched context")
    except json.JSONDecodeError:
        # Fallback if the input isn't valid JSON - treat it as simple content
        logger.warning(f"Invalid JSON input to scene_description, using as plain text")
        enriched_prompt = context_json
    
    agent = Agent(
        name="SceneDescTool",
        instructions=(
            "You are a senior visual designer crafting prompts for DALL·E.\n\n"
            "INPUT: JSON with keys:\n"
            "  • content          (string)  — the post caption\n"
            "  • company_context  (object)  — includes tone_of_voice (e.g. friendly, witty), color palette or vibe\n"
            "  • brand_hero       (string)  — the mascot’s description (do not alter this text)\n\n"
            "TASK: Write one richly detailed scene description that a DALL·E model can consume directly.  "
            "Do not create description more than 950 characters, not more than max lenth.\n"
            "Include:\n"
            "  – Environment & setting: time of day, location, background details.\n"
            "  – Composition & perspective: camera angle, focal point.\n"
            "  – Lighting & color palette: mood through light, hues, contrast.\n"
            "  – Action & props: what’s happening, any objects or activities that reinforce the caption.\n"
            "  – Mascot integration: describe *exactly* how the brand hero appears—"
            "   Prepared description of the mascot with maximum length of 950 characters.\n"
            "  It’s should be written as one single, hyper-detailed paragraph so DALL·E has everything it needs to render a perfect brand-hero illustration.\n"
            "e.g. perched on a surface, interacting with an object, subtly placed in the frame—"
            "matching the company’s tone.\n\n"
            "OUTPUT: a single paragraph plain-text description—no JSON, no code fences."
        )
    )
    res = await Runner.run(agent, enriched_prompt)
    try:
        obj = json.loads(res.final_output)
        return {"scene_description": obj.get("scene_description", "")}    
    except Exception:
        # Fallback: wrap plain text
        return {"scene_description": res.final_output.strip()}


class ImageAgent:
    def __init__(self):
        self.agent = Agent(
            name='ImageAgent',
            instructions=(
                'Follow these steps: 1) Use the scene_description tool on the input context; '
                '2) Use the generate_image tool on the returned description; '
                '3) Return exactly a JSON dict with keys scene_description and image_url.'
            ),
            tools=[scene_description, generate_image]
        )

    async def run(self, context: str) -> Dict[str, str]:
        # Context can now be either a simple string (backward compatibility) 
        # or a JSON string with content and company data
        result = await Runner.run(self.agent, context)
        output = result.final_output
        try:
            out = json.loads(output)
            return {
                'scene_description': out.get('scene_description', ''),
                'image_url': out.get('image_url', '')
            }
        except Exception:
            parts = output.splitlines()
            return {
                'scene_description': parts[0] if parts else '',
                'image_url': parts[1] if len(parts) > 1 else ''
            }