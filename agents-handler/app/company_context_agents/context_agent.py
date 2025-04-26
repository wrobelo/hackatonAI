from agents import Agent, Runner, function_tool, ModelSettings
from typing import Optional, Dict, Any, List
from pymongo import MongoClient
import os
import logging
import datetime
from app.company_context_agents.prompts import get_company_context_prompt
from qdrant_client import QdrantClient
from qdrant_client.http import models

logger = logging.getLogger(__name__)

# MongoDB setup
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
mongo_client = MongoClient(MONGODB_URI)
mongo_db = mongo_client[os.getenv("MONGO_DB", "brand-hero")]
company_context_collection = mongo_db["company_context_memory"]

# Qdrant setup
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "brand_hero")
qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

@function_tool
async def fetch_vector_db(company_id: str) -> Optional[str]:
    """
    Pobiera wstępne informacje z wektorowej bazy Qdrant.
    Wyszukuje dokumenty po metadanych company_id i type="data".
    Zwraca surowy tekst lub None, jeśli brak danych.
    """
    try:
        # Wyszukiwanie dokumentów po metadanych
        search_result = qdrant_client.scroll(
            collection_name=QDRANT_COLLECTION,
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="metadata.company_id",
                        match=models.MatchValue(value=company_id)
                    ),
                    models.FieldCondition(
                        key="metadata.type",
                        match=models.MatchValue(value="data")
                    )
                ]
            ),
            limit=100  # Maksymalna liczba dokumentów do pobrania
        )
        
        # Sprawdź czy znaleziono dokumenty
        if not search_result or not search_result[0]:
            logger.warning(f"No documents found in Qdrant for company_id={company_id} and type=data")
            return None
            
        # Połącz zawartość wszystkich znalezionych dokumentów
        documents = search_result[0]
        content = []
        
        for doc in documents:
            if doc.payload and "content" in doc.payload:
                content.append(doc.payload["content"])
        
        if not content:
            logger.warning(f"Documents found but no content available for company_id={company_id}")
            return None
            
        # Połącz wszystkie treści w jeden tekst
        return "\n\n".join(content)
        
    except Exception as e:
        logger.error(f"Error fetching data from Qdrant: {str(e)}")
        return None

@function_tool
async def fetch_sql_db(company_id: str) -> Optional[str]:
    """
    Pobiera wstępne informacje z SQL (tabela companies).
    Zwraca surowy tekst lub None.
    """
    # … tu logika połączenia z SQL …
    return ""  # przykład

@function_tool
async def store_context(company_id: str, context_description: str) -> None:
    """
    Zapisuje ostateczny opis firmy w bazie MongoDB.
    """
    try:
        # Pobierz aktualny dokument, aby zachować previous_response_id
        doc = company_context_collection.find_one({"company_id": company_id})
        previous_response_id = doc.get("previous_response_id") if doc else None
        
        # Aktualizacja lub utworzenie dokumentu z kontekstem firmy
        company_context_collection.update_one(
            {"company_id": company_id},
            {"$set": {
                "context_description": context_description,
                "previous_response_id": previous_response_id,
                "updated_at": datetime.datetime.utcnow()
            }},
            upsert=True
        )
        logger.info(f"Saved context for company_id={company_id} to MongoDB")
    except Exception as e:
        logger.error(f"Error saving context to MongoDB: {str(e)}")
        raise

async def dynamic_instructions(wrapper, agent) -> str:
    cid = wrapper.context['company_id']
    return get_company_context_prompt(cid)

class CompanyContextAgent:
    def __init__(self):
        logger.info("Initializing CompanyContextAgent")
        self.agent = Agent(
            name="CompanyContextCollector",
            instructions=dynamic_instructions,
            model="o4-mini",
            tools=[fetch_vector_db, fetch_sql_db, store_context],
            model_settings=ModelSettings(tool_choice="auto"),  # pozwól LLM decydować
        )

    async def run(self, company_id: str, user_response: Optional[str] = None) -> Dict[str, Any]:
        """
        Uruchamia agenta zbierającego kontekst firmy.
        
        Args:
            company_id: Identyfikator firmy
            user_response: Opcjonalna odpowiedź użytkownika na pytanie agenta
            
        Returns:
            Słownik zawierający wynik działania agenta i identyfikator ostatniej odpowiedzi
        """
        # 1. Zbuduj kontekst dla agenta
        context = {"company_id": company_id}
        
        # 2. Pobierz poprzedni identyfikator odpowiedzi z MongoDB
        doc = company_context_collection.find_one({"company_id": company_id})
        previous_response_id = doc.get("previous_response_id") if doc else None
        
        # Jeśli mamy odpowiedź użytkownika i poprzedni identyfikator odpowiedzi,
        # przekazujemy je do agenta
        if user_response and previous_response_id:
            # Uruchom agenta z kontekstem i odpowiedzią użytkownika
            logger.info(f"Running agent with user response for company {company_id}")
            result = await Runner.run(
                self.agent,
                context=context,
                previous_response_id=previous_response_id,
                input=user_response
            )
        else:
            # Pierwsze uruchomienie - bez odpowiedzi użytkownika
            logger.info(f"Running agent for first time for company {company_id}")
            result = await Runner.run(
                self.agent,
                context=context,
                input=""
            )

        # 4. Wyciągnij nowy previous_response_id z wyniku (jeśli jest)
        last_response_id = getattr(result, 'last_response_id', None)

        # 5. Zaktualizuj MongoDB, jeśli jest nowy previous_response_id
        if last_response_id:
            company_context_collection.update_one(
                {"company_id": company_id},
                {"$set": {"previous_response_id": last_response_id}},
                upsert=True
            )
            logger.info(f"Updated previous_response_id for company {company_id}")

        return {
            "output": getattr(result, 'final_output', None),
            "previous_response_id": last_response_id
        }

# Inicjalizacja agenta dla importu w api.py
agent_instance = CompanyContextAgent()
agent = agent_instance.agent
runner = Runner()

# Funkcja opakowująca dla zachowania kompatybilności z istniejącym kodem
async def run_company_context_agent(agent, company_id, user_response=None):
    """
    Funkcja opakowująca dla zachowania kompatybilności z istniejącym kodem.
    """
    return await agent_instance.run(company_id, user_response)
