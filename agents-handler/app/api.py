import os
import logging
from openai import OpenAI

from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, HTTPException
from typing import List
from app.schemas import GeneratePostsRequest, PostProposal
from app.agents.post_generator.post_orchestrator import PostOrchestratorAgent
from app.agents.research.strategy_agent import StrategyAgent  # Import the StrategyAgent

# Load .env at module import
base_dir = os.path.dirname(os.path.dirname(__file__))
dotenv_path = os.path.join(base_dir, '.env')
load_dotenv(dotenv_path)

router = APIRouter()
postAgent = PostOrchestratorAgent()

# Initialize the strategy agent
strategyAgent = StrategyAgent()

app = FastAPI()
app.include_router(router, prefix='/api')


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


client = OpenAI()
client.api_key = os.getenv("OPENAI_API_KEY")
@app.get("/test-image")
async def test_image():
    try:
        img_resp = client.images.generate(prompt="A simple blue circle on a white background",
        n=1,
        size="512x512")
        return {"success": True, "url": img_resp.data[0].url}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/posts/{company_id}", response_model=List[PostProposal])
async def get_posts(company_id: str):
    """
    Generate 3/5/7 social-media posts for the given company_id.
    All inputs (strategy, tone, mascot) are fetched from MongoDB.
    """
    try:
        proposals = await postAgent.generate(company_id)
        return proposals
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/strategy/{company_id}")
async def get_strategy(company_id: str):
    try:
        logger.info(f"Generating strategy for company_id: {company_id}")
        result = await strategyAgent.propose(company_id)
        return result
    except ValueError as e:
        logger.error(f"Strategy generation error: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception(f"Strategy generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Strategy generation failed: {str(e)}")
