import os
from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, HTTPException
from app.schemas import GeneratePostsRequest, PostProposal, CompanyContextRequest, CompanyContextResponse, BrandHeroContextRequest, BrandHeroContextResponse
from app.agents.orchestrator import OrchestratorAgent
from app.db.company_context_db import get_company_context, get_brandhero_context, retrieve_image_from_gridfs
import importlib.util
import sys

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

from app.brandheroagents.brandhero_orchestrator import BrandHeroOrchestratorAgent

# Load .env at module import
base_dir = os.path.dirname(os.path.dirname(__file__))
dotenv_path = os.path.join(base_dir, '.env')
load_dotenv(dotenv_path)

router = APIRouter()
ag = OrchestratorAgent()
bag = BrandHeroOrchestratorAgent()

client = OpenAI()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
mongo_client = MongoClient(MONGODB_URI)
mongo_db_name="brand-hero"
mongo_db = mongo_client[os.getenv("MONGODB_DB", mongo_db_name)]
collection_name="images"
client = MongoClient(MONGODB_URI)
db = client[mongo_db_name]
fs = gridfs.GridFS(db)


@router.post('/generate-posts', response_model=list[PostProposal])
async def generate_posts(req: GeneratePostsRequest):
    try:
        return await ag.generate(req.dict())
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


app = FastAPI()
app.include_router(router, prefix='/api')
