from agents import Agent, Runner, function_tool, ModelSettings
from typing import Optional, Dict, Any, List
import logging
from app.company_context_agents.prompts import get_company_context_prompt
from app.db.company_context_db import update_company_context, get_company_context, get_initial_company_data

logger = logging.getLogger(__name__)


@function_tool
async def get_initial_data_from_db(company_id: str) -> Optional[str]:
    """
    Pobiera wstępne informacje o firmie z kolekcji company_initial_collection.
    Zwraca surowy tekst lub None, jeśli brak danych.
    """
    try:
        # Pobierz wstępne dane firmy z MongoDB
        doc = await get_initial_company_data(company_id)
        
        # Jeśli dokument nie istnieje, zwróć None
        if not doc:
            logger.warning(f"No initial data found for company_id={company_id}")
            return None
        
        # Przygotuj tekst z danymi firmy
        result = []
        
        # Dodaj wszystkie pola dokumentu do wyniku, pomijając _id i company_id
        for key, value in doc.items():
            if key not in ["_id", "company_id"]:
                result.append(f"{key}: {value}")
        
        if not result:
            logger.warning(f"Initial data found but no useful fields for company_id={company_id}")
            return None
            
        return "\n".join(result)
        
    except Exception as e:
        logger.error(f"Error fetching initial data from MongoDB: {str(e)}")
        return None

@function_tool
async def fetch_sql_db(company_id: str) -> Optional[str]:
    """
    Pobiera wstępne informacje z SQL (tabela companies) oraz aktualny kontekst firmy.
    Zwraca surowy tekst lub None.
    """
    try:
        # Pobierz aktualny kontekst firmy z MongoDB
        from app.db.company_context_db import get_company_context
        doc = await get_company_context(company_id)
        
        # Jeśli istnieje kontekst, zwróć go
        if doc and "context_description" in doc:
            logger.info(f"Retrieved existing context for company_id={company_id}")
            return f"Aktualny kontekst firmy:\n{doc['context_description']}"
        
        # Tutaj można dodać logikę pobierania danych z SQL, jeśli nie ma kontekstu
        
        return "Brak danych w bazie SQL i brak istniejącego kontekstu."
    except Exception as e:
        logger.error(f"Error fetching data from SQL/MongoDB: {str(e)}")
        return None

@function_tool
async def store_context(company_id: str, context_description: str) -> None:
    """
    Zapisuje ostateczny opis firmy w bazie MongoDB.
    """
    try:
        # Użyj funkcji z modułu company_context_db do aktualizacji kontekstu
        success = await update_company_context(company_id, context_description)
        
        if not success:
            logger.error(f"Failed to save context for company_id={company_id}")
            raise Exception(f"Failed to save context for company_id={company_id}")
            
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
            tools=[get_initial_data_from_db, fetch_sql_db, store_context],
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
        # Użyj funkcji z modułu company_context_db
        from app.db.company_context_db import get_company_context
        doc = await get_company_context(company_id)
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
            # Pobierz aktualny kontekst, jeśli istnieje
            doc = await get_company_context(company_id)
            context_description = doc.get("context_description", "") if doc else ""
            
            # Aktualizuj dokument z nowym previous_response_id
            await update_company_context(company_id, context_description, last_response_id)
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
