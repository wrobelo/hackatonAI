from typing import Optional, Dict, Any
import logging
from pymongo import MongoClient
import os
import datetime

logger = logging.getLogger(__name__)

# MongoDB setup
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
mongo_client = MongoClient(MONGODB_URI)
mongo_db = mongo_client[os.getenv("MONGO_DB", "brand-hero")]
company_context_collection = mongo_db["company_context_memory"]
company_initial_collection = mongo_db["company_initial_memory"]

async def get_initial_company_data(company_id: str) -> Optional[Dict[str, Any]]:
    """
    Pobiera wstępne dane firmy z kolekcji company_initial_collection na podstawie company_id.
    
    Args:
        company_id: Identyfikator firmy
        
    Returns:
        Słownik zawierający wstępne dane firmy lub None, jeśli nie znaleziono
    """
    try:
        # Pobierz dokument z MongoDB
        doc = company_initial_collection.find_one({"company_id": company_id})
        
        if not doc:
            logger.warning(f"Initial data for company_id {company_id} not found")
            return None
        
        return doc
    except Exception as e:
        logger.error(f"Error retrieving initial company data from MongoDB: {str(e)}")
        return None

async def get_company_context(company_id: str) -> Optional[Dict[str, Any]]:
    """
    Pobiera kontekst firmy z bazy MongoDB na podstawie company_id.
    
    Args:
        company_id: Identyfikator firmy
        
    Returns:
        Słownik zawierający dane kontekstu firmy lub None, jeśli nie znaleziono
    """
    try:
        # Pobierz dokument z MongoDB
        doc = company_context_collection.find_one({"company_id": company_id})
        
        # Jeśli dokument nie istnieje lub nie ma context_description, zwróć None
        if not doc or "context_description" not in doc:
            logger.warning(f"Context for company_id {company_id} not found")
            return None
        
        return doc
    except Exception as e:
        logger.error(f"Error retrieving company context from MongoDB: {str(e)}")
        return None

async def update_company_context(company_id: str, context_description: str, previous_response_id: Optional[str] = None) -> bool:
    """
    Aktualizuje lub tworzy kontekst firmy w bazie MongoDB.
    
    Args:
        company_id: Identyfikator firmy
        context_description: Opis kontekstu firmy
        previous_response_id: Opcjonalny identyfikator poprzedniej odpowiedzi
        
    Returns:
        True jeśli operacja się powiodła, False w przeciwnym razie
    """
    try:
        # Jeśli previous_response_id nie został podany, pobierz go z istniejącego dokumentu
        if previous_response_id is None:
            doc = company_context_collection.find_one({"company_id": company_id})
            previous_response_id = doc.get("previous_response_id") if doc else None
        
        # Przygotuj dane do aktualizacji
        update_data = {
            "context_description": context_description,
            "updated_at": datetime.datetime.utcnow()
        }
        
        # Dodaj previous_response_id, jeśli istnieje
        if previous_response_id:
            update_data["previous_response_id"] = previous_response_id
        
        # Aktualizacja lub utworzenie dokumentu
        company_context_collection.update_one(
            {"company_id": company_id},
            {"$set": update_data},
            upsert=True
        )
        
        logger.info(f"Updated context for company_id={company_id} in MongoDB")
        return True
    except Exception as e:
        logger.error(f"Error updating company context in MongoDB: {str(e)}")
        return False
