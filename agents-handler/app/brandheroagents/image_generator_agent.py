import logging
import openai
import json
from typing import Dict
from agents import Agent, Runner, function_tool
from openai import OpenAI
import requests

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class BrandHeroImageGenerationAgent:
    def __init__(self):
        self.agent = Agent(
            name='BrandHeroImageGenerationAgent',
            instructions="""Follow these steps:
                1. Generate an image basing on description
            """,
            tools=[generate_brand_hero_image]

        )
    async def run(self, prompt: str, company: str) -> str:
        logger.info("Starting image generation for: %s", prompt)
        try:
            result =  generate_brand_hero_image(prompt, company)
            logger.info("result: %s", result)

            return result

        except Exception as e:
            logger.exception("Error in image generation", e)
            raise

def generate_brand_hero_image(prompt: str, company: str) -> str:
    client = OpenAI()
    messages=[
        {"role": "system", "content": "Jesteś pomocnikiem tworzącym wysokiej jakości prompty do DALL·E 3. Ulepszaj opisy postaci, dodając szczegóły dotyczące wyglądu, emocji, otoczenia, kompozycji i stylu graficznego."},
        {"role": "system", "content":"A brand hero is a personification of a brand – a character (real or fictional) that represents the brand’s values, personality, and way of communicating with its audience. The brand hero acts as the 'face of the brand' and can appear in advertisements,"
                                     " on packaging, websites, and social media. Its main goal is to build emotional connections with customers, strengthen brand recognition, and make the brand stand out from the competition."},
        {"role": "system", "content":"Good brand hero should be simple. Should be easy to use in all forms of advertisements."},
        {"role": "system", "content":"Reduce details."},
        {"role": "user", "content": prompt},
        {"role": "system", "content": f"Generate detailed prompt do DALL·E to generate image of brand hero of company described: {company}"}
    ]


    for message in messages:
        thread.add(message["role"], message["content"])

    gpt_response = client.chat.completions.create(
        model="gpt-4.1",
        messages=messages
    )

    dalle_prompt = gpt_response.choices[0].message.content
    thread.add("assistant", dalle_prompt)

    image_response = client.images.generate(
        model="dall-e-3",
        prompt=dalle_prompt,
        size="1024x1024",
        quality="standard",
        n=1
    )

    image_url = image_response.data[0].url
    logger.info("Obrazek dostępny pod adresem: %s", image_url)
    return image_url



def describe_brand_hero(url: str) -> str:
    image_url = url

    if not image_url:
        print("No URL found in the generate result")
        return None
    # Download the image
    response = requests.get(image_url, stream=False)
    response.raise_for_status()  # Raise exception for HTTP errors
