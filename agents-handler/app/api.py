import os
from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, HTTPException
from app.schemas import GeneratePostsRequest, PostProposal, CompanyContextRequest, CompanyContextResponse
from app.agents.orchestrator import OrchestratorAgent
import importlib.util
import sys
import os





# Dynamic import for agent and runner from app/company-context-agents/context_agent.py
context_agent_path = os.path.join(os.path.dirname(__file__), "company_context_agents", "context_agent.py")
spec = importlib.util.spec_from_file_location("context_agent", context_agent_path)
context_agent = importlib.util.module_from_spec(spec)
sys.modules["context_agent"] = context_agent
spec.loader.exec_module(context_agent)
agent = context_agent.agent
runner = context_agent.runner
run_company_context_agent_wrapper = context_agent.run_company_context_agent

# Load .env at module import
base_dir = os.path.dirname(os.path.dirname(__file__))
dotenv_path = os.path.join(base_dir, '.env')
load_dotenv(dotenv_path)

router = APIRouter()
ag = OrchestratorAgent()

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
async def get_company_context(company_id: str):
    try:
        # Pobierz dokument z MongoDB
        doc = context_agent.company_context_collection.find_one({"company_id": company_id})
        
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

app = FastAPI()
app.include_router(router, prefix='/api')
