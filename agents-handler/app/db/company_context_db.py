from typing import Optional, Dict, Any, Tuple
import logging
from pymongo import MongoClient
import os
import datetime
import requests
import base64
import gridfs
from bson.objectid import ObjectId

logger = logging.getLogger(__name__)

# MongoDB setup
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
mongo_client = MongoClient(MONGODB_URI)
mongo_db = mongo_client[os.getenv("MONGO_DB", "brand-hero")]
company_context_collection = mongo_db["company_context_memory"]
company_initial_collection = mongo_db["company_initial_memory"]
company_brandhero_collection = mongo_db["company_brandhero_memory"]

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

async def get_brandhero_context(company_id: str) -> Optional[Dict[str, Any]]:
    """
    Pobiera kontekst brand hero z bazy MongoDB na podstawie company_id.
    
    Args:
        company_id: Identyfikator firmy
        
    Returns:
        Słownik zawierający dane kontekstu brand hero lub None, jeśli nie znaleziono
    """
    try:
        # Pobierz dokument z MongoDB
        doc = company_brandhero_collection.find_one({"company_id": company_id})
        
        # Jeśli dokument nie istnieje lub nie ma brandhero_context, zwróć None
        if not doc or "brandhero_context" not in doc:
            logger.warning(f"Brand hero context for company_id {company_id} not found")
            return None
        
        return doc
    except Exception as e:
        logger.error(f"Error retrieving brand hero context from MongoDB: {str(e)}")
        return None

async def store_image_in_gridfs(
    image_url: str,
    company_id: str,
    description: Optional[str] = None,
    source: str = "brand_hero_generator"
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Pobiera obraz z URL, zapisuje go w GridFS i zwraca ID pliku oraz base64 obrazu.
    
    Args:
        image_url: URL obrazu do pobrania
        company_id: Identyfikator firmy
        description: Opcjonalny opis obrazu
        source: Źródło obrazu (domyślnie "brand_hero_generator")
        
    Returns:
        Tuple zawierający:
        - bool: True jeśli operacja się powiodła, False w przeciwnym razie
        - Optional[str]: ID pliku w GridFS lub None w przypadku błędu
        - Optional[str]: Obraz w formacie base64 lub None w przypadku błędu
    """
    try:
        # Inicjalizacja GridFS
        fs = gridfs.GridFS(mongo_db)
        
        # Pobierz obraz
        response = requests.get(image_url)
        if response.status_code != 200:
            logger.error(f"Failed to download image from URL: {image_url}")
            return False, None, None
        
        image_data = response.content
        
        # Zapisz obraz w GridFS
        metadata = {
            "company_id": company_id,
            "content_type": response.headers.get("Content-Type", "image/jpeg"),
            "description": description,
            "source": source
        }
        
        file_id = fs.put(image_data, filename=f"brand_hero_{company_id}.jpg", metadata=metadata)
        
        # Konwertuj obraz do base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        logger.info(f"Image stored in GridFS with ID: {file_id}")
        return True, str(file_id), image_base64
    except Exception as e:
        logger.error(f"Error storing image in GridFS: {str(e)}")
        return False, None, None

async def retrieve_image_from_gridfs(file_id: str) -> Tuple[Optional[bytes], Optional[str]]:
    """
    Pobiera obraz z GridFS na podstawie ID pliku.
    
    Args:
        file_id: ID pliku w GridFS
        
    Returns:
        Tuple zawierający:
        - Optional[bytes]: Dane obrazu lub None w przypadku błędu
        - Optional[str]: Typ zawartości (content type) lub None w przypadku błędu
    """
    try:
        # Inicjalizacja GridFS
        fs = gridfs.GridFS(mongo_db)
        
        # Pobierz obraz
        grid_out = fs.get(ObjectId(file_id))
        
        # Pobierz typ zawartości z metadanych
        content_type = None
        if hasattr(grid_out, 'metadata') and grid_out.metadata and 'content_type' in grid_out.metadata:
            content_type = grid_out.metadata['content_type']
        else:
            content_type = 'image/jpeg'
        
        return grid_out.read(), content_type
    except Exception as e:
        logger.error(f"Error retrieving image from GridFS: {str(e)}")
        return None, None

async def update_brandhero_context(
    company_id: str, 
    brandhero_context: str, 
    previous_response_id: Optional[str] = None,
    brandhero_description: Optional[str] = None,
    image_url: Optional[str] = None
) -> bool:
    """
    Aktualizuje lub tworzy kontekst brand hero w bazie MongoDB.
    
    Args:
        company_id: Identyfikator firmy
        brandhero_context: Opis kontekstu brand hero
        previous_response_id: Opcjonalny identyfikator poprzedniej odpowiedzi
        brandhero_description: Opcjonalny szczegółowy opis brand hero na podstawie wygenerowanego obrazu
        image_url: Opcjonalny URL do wygenerowanego obrazu brand hero
        
    Returns:
        True jeśli operacja się powiodła, False w przeciwnym razie
    """
    try:
        # Jeśli previous_response_id nie został podany, pobierz go z istniejącego dokumentu
        if previous_response_id is None:
            doc = company_brandhero_collection.find_one({"company_id": company_id})
            previous_response_id = doc.get("previous_response_id") if doc else None
        
        # Przygotuj dane do aktualizacji
        update_data = {
            "brandhero_context": brandhero_context,
            "updated_at": datetime.datetime.utcnow()
        }
        
        # Dodaj opcjonalne pola, jeśli istnieją
        if previous_response_id:
            update_data["previous_response_id"] = previous_response_id
        
        if brandhero_description:
            update_data["brandhero_description"] = brandhero_description
            
        if image_url:
            update_data["image_url"] = image_url
        
        # Aktualizacja lub utworzenie dokumentu
        company_brandhero_collection.update_one(
            {"company_id": company_id},
            {"$set": update_data},
            upsert=True
        )
        
        logger.info(f"Updated brand hero context for company_id={company_id} in MongoDB")
        return True
    except Exception as e:
        logger.error(f"Error updating brand hero context in MongoDB: {str(e)}")
        return False
