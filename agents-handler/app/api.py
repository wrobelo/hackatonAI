import os
import logging
from openai import OpenAI
from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, HTTPException
from typing import List
from app.schemas import GeneratePostsRequest, PostProposal, CompanyContextRequest, StrategyRequest, PostEditRequest, StrategyResponse,CompanyContextResponse, BrandHeroContextRequest, BrandHeroContextResponse
from app.agents.post_generator.post_orchestrator import PostOrchestratorAgent
from app.agents.research.strategy_agent import StrategyAgent, mongo_db, get_strategy_by_company_id  # Import the StrategyAgent, mongo_db and get_strategy_by_company_id
from app.db.company_context_db import get_company_context, get_brandhero_context, retrieve_image_from_gridfs

import importlib.util
import sys
import os
import gridfs
from pymongo import MongoClient
from bson.objectid import ObjectId
from fastapi.responses import StreamingResponse
import io
from openai import OpenAI

# Dynamic import for agent and runner from app/company-context-agents/context_agent.py
context_agent_path = os.path.join(os.path.dirname(__file__), "company_context_agents", "context_agent.py")
spec = importlib.util.spec_from_file_location("context_agent", context_agent_path)
context_agent = importlib.util.module_from_spec(spec)
sys.modules["context_agent"] = context_agent
spec.loader.exec_module(context_agent)
agent = context_agent.agent
runner = context_agent.runner
run_company_context_agent_wrapper = context_agent.run_company_context_agent

bh_agent_path = os.path.join(os.path.dirname(__file__), "bhagents", "bh_agent.py")
spec_bh = importlib.util.spec_from_file_location("bh_agent", bh_agent_path)
bh_agent = importlib.util.module_from_spec(spec_bh)
sys.modules["bh_agent"] = bh_agent
spec_bh.loader.exec_module(bh_agent)
agentbh = bh_agent.agent
runnerbh = bh_agent.runner
run_run_bh_agent_wrapper = bh_agent.run_bh_agent


# Load .env at module import
base_dir = os.path.dirname(os.path.dirname(__file__))
dotenv_path = os.path.join(base_dir, '.env')
load_dotenv(dotenv_path)

router = APIRouter()
postAgent = PostOrchestratorAgent()

client = OpenAI()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
mongo_client = MongoClient(MONGODB_URI)
mongo_db_name="brand-hero"
mongo_db = mongo_client[os.getenv("MONGODB_DB", mongo_db_name)]
collection_name="images"
client = MongoClient(MONGODB_URI)
db = client[mongo_db_name]
fs = gridfs.GridFS(db)


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
        img_resp = client.images.generate(
        prompt="A simple blue circle on a white background",
        n=1,
        size="512x512")
        return {"success": True, "url": img_resp.data[0].url}
    except Exception as e:
        return {"success": False, "error": str(e)}
 
@app.get("/api/posts/{company_id}", response_model=List[PostProposal])
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

@router.post('/company-context/{company_id}')
async def run_company_context_agent(company_id: str, request: CompanyContextRequest = None):
    try:
        # Przekazujemy odpowiedź użytkownika, jeśli istnieje
        user_response = request.user_response if request and request.user_response else None
        result = await run_company_context_agent_wrapper(agent, company_id, user_response)
        
        return {"company_id": company_id, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 

@router.get('/company-context/{company_id}', response_model=CompanyContextResponse)
async def get_company_context_endpoint(company_id: str):
    try:
        # Pobierz dokument z MongoDB
        doc = await get_company_context(company_id)

        # Jeśli dokument nie istnieje lub nie ma context_description, zwróć 404
        if not doc or "context_description" not in doc:
            raise HTTPException(status_code=404, detail=f"Context for company_id {company_id} not found")

        # Zwróć context_description
        return {
            "company_id": company_id,
            "context_description": doc["context_description"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/brand-hero-context/{company_id}')
async def run_brand_hero_context_agent(company_id: str, request: BrandHeroContextRequest = None):
    try:
        # Przekazujemy odpowiedź użytkownika, jeśli istnieje
        user_response = request.user_response if request and request.user_response else None
        result = await run_run_bh_agent_wrapper(agentbh, company_id, user_response)

        return {"company_id": company_id, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/brand-hero-context/{company_id}', response_model=BrandHeroContextResponse)
async def get_brand_hero_context_endpoint(company_id: str):
    try:
        # Pobierz dokument z MongoDB
        doc = await get_brandhero_context(company_id)
        
        # Jeśli dokument nie istnieje lub nie ma brandhero_context, zwróć 404
        if not doc or "brandhero_context" not in doc:
            raise HTTPException(status_code=404, detail=f"Brand hero context for company_id {company_id} not found")
        
        # Przygotuj odpowiedź
        response = {
            "company_id": company_id,
            "brandhero_context": doc["brandhero_context"]
        }
        
        # Dodaj opcjonalne pola, jeśli istnieją
        if "brandhero_description" in doc:
            response["brandhero_description"] = doc["brandhero_description"]
            
        if "image_url" in doc:
            response["image_url"] = doc["image_url"]
            
            # No need to include base64 image data in the response
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/images/{file_id}")
async def get_image(file_id: str):
    image_data, content_type = await retrieve_image_from_gridfs(file_id)

    if not image_data:
        raise HTTPException(status_code=404, detail=f"Image with ID {file_id} not found")

    return StreamingResponse(io.BytesIO(image_data), media_type=content_type)





@router.post("/strategy/{company_id}")
async def run_strategy_agent(company_id: str, request: StrategyRequest = None):
    try:
        logger.info(f"Working on strategy for company_id: {company_id}")
        
        # Pass the user response if it exists
        user_response = request.user_response if request and request.user_response else None
        
        # Update the strategyAgent to accept user responses
        result = await strategyAgent.run(company_id, user_response)
        
        return {"company_id": company_id, "result": result}
    except ValueError as e:
        logger.error(f"Strategy generation error: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception(f"Strategy generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Strategy generation failed: {str(e)}")
    
@router.post("/posts/edit")
async def edit_post(request: PostEditRequest):
    try:
        logger.info(f"Editing post for company_id: {request.company_id}")
        
        # Prepare post data with conversation_id if provided
        post_data = request.post
        if request.conversation_id:
            post_data["conversation_id"] = request.conversation_id
        
        # Call the edit_post method on the PostOrchestratorAgent with company_id
        result = await postAgent.edit_post(
            post_data=post_data, 
            company_id=request.company_id,
            user_response=request.user_response
        )
        
        return {
            "conversation_id": result["conversation_id"],
            "company_id": result["company_id"],
            "result": result
        }
    except ValueError as e:
        logger.error(f"Post edit error: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception(f"Post edit failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Post edit failed: {str(e)}")

@router.get("/strategy/{company_id}", response_model=StrategyResponse)
async def get_strategy(company_id: str):
    """
    Get the strategy for a specific company by company_id.
    Returns the strategy from MongoDB.
    """
    try:
        logger.info(f"Fetching strategy for company_id: {company_id}")
        
        # Call the get_strategy_by_company_id function from strategy_agent.py
        result, status_code = await get_strategy_by_company_id(company_id)
        
        if status_code != 200:
            if status_code == 404:
                raise HTTPException(status_code=404, detail=result.get("error", "Strategy not found"))
            else:
                raise HTTPException(status_code=500, detail=result.get("error", "Error fetching strategy"))
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error fetching strategy: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching strategy: {str(e)}")

app = FastAPI()
app.include_router(router, prefix='/api')