import logging
import openai
from typing import List
from agents import Agent, Runner, function_tool, handoff
from app.brandheroagents.image_generator_agent import BrandHeroImageGenerationAgent
from app.brandheroagents.save_image_agent import SaveImageAgent, SaveImage
from typing import Dict
from app.schemas import PostProposal, ResearchReport, PostDraft,SaveImage, GenerateBrandHeroImageResponse
from openai import OpenAI


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class BrandHeroOrchestratorAgent:
    def __init__(self):
        logger.info("Initializing BrandHeroOrchestratorAgent")
        self.generateBrandHeroImage = BrandHeroImageGenerationAgent()
        self.save = SaveImageAgent()

    async def generate(self, req: dict) -> GenerateBrandHeroImageResponse:
        client = OpenAI()
        logger.info("Running BrandHeroOrchestratorAgent for: %s", req)
        try:
            image: str = await self.generateBrandHeroImage.run(req.get('prompt'), req.get('company'))
            logger.info("Image generated: %s", image)


            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text",
                         "text": "Przygotuj mi bardzo dokładny opis postaci na obrazku."
                                 " Chcę by opis dokłądnie odzwierciedlał zarówno wygląd zewnętrzny jak i cechy charakteru postaci."
                                 " Pamiętaj, żeby na podstawie opisu dało się dokładnie odtworzyć stylistykę pierwotnego obrazu"
                                 " Chcę wykorzystywać opis do tworzenia kolejnych obrazów tej postaci podczas różncyh czynności"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"{image}"

                            },
                        },
                    ],
                }
            ]
            gpt_response = client.chat.completions.create(
                model="gpt-4.1",
                messages=messages,
                max_tokens=1000,
            )
        except Exception as e:
            logger.exception("Error during content drafting step")
            raise
        try:
            save_image = SaveImage(
                image_url=image,
                contextId=req.get("contextId"),
                description=gpt_response.choices[0].message.content

            )
            await self.save.run(save_image)
            response = GenerateBrandHeroImageResponse(
                contextId = req.get("contextId")
            )
            return response
        except Exception as e:
            logger.exception("Error during content drafting step")
            raise

    def retrieve_image_from_mongodb(self, file_id):
        return self.save.retrieve_image_from_mongodb(file_id)
