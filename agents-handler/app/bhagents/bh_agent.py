from agents import Agent, Runner, function_tool, ModelSettings
from typing import Optional, Dict, Any
import os
import logging
import datetime
from app.bhagents.prompts import get_brand_hero_prompt
from openai import OpenAI
from app.db.company_context_db import (
    get_company_context, 
    get_brandhero_context, 
    update_brandhero_context,
    store_image_in_gridfs
)

logger = logging.getLogger(__name__)

@function_tool
async def store_context(company_id: str, context_description: str) -> None:
    """
    Zapisuje kontekst brand hero w bazie MongoDB.
    """
    try:
        # Użyj funkcji z modułu company_context_db do aktualizacji kontekstu
        success = await update_brandhero_context(
            company_id=company_id, 
            brandhero_context=context_description
        )
        
        if not success:
            logger.error(f"Failed to save brand hero context for company_id={company_id}")
            raise Exception(f"Failed to save brand hero context for company_id={company_id}")
            
        logger.info(f"Saved brand hero context for company_id={company_id} to MongoDB")
    except Exception as e:
        logger.error(f"Error saving brand hero context to MongoDB: {str(e)}")
        raise

@function_tool
async def generate_brand_hero(company_id: str) -> str:
    """
    Generuje obraz brand hero, analizuje go i zapisuje w bazie MongoDB.
    Zwraca szczegółowy opis wygenerowanego obrazu.
    """
    try:
        # Pobierz aktualny kontekst brand hero
        doc = await get_brandhero_context(company_id)
        
        if not doc or "brandhero_context" not in doc:
            logger.error(f"No brand hero context found for company_id={company_id}")
            return "Nie znaleziono kontekstu brand hero. Najpierw zapisz kontekst używając store_context."
        
        brandhero_context = doc["brandhero_context"]
        previous_response_id = doc.get("previous_response_id")
        
        # Generuj prompt do DALL-E
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Generuj prompt do DALL-E
        messages = [
            {"role": "system", "content": "Jesteś pomocnikiem tworzącym wysokiej jakości prompty do DALL·E 3. Ulepszaj opisy postaci, dodając szczegóły dotyczące wyglądu, emocji, otoczenia, kompozycji i stylu graficznego."},
            {"role": "system", "content": "A brand hero is a personification of a brand – a character (real or fictional) that represents the brand's values, personality, and way of communicating with its audience. The brand hero acts as the 'face of the brand' and can appear in advertisements, on packaging, websites, and social media. Its main goal is to build emotional connections with customers, strengthen brand recognition, and make the brand stand out from the competition."},
            {"role": "system", "content": "Good brand hero should be simple. Should be easy to use in all forms of advertisements."},
            {"role": "system", "content": "Reduce details."},
            {"role": "system", "content": f"Generate detailed prompt for DALL·E to generate image of brand hero described as: {brandhero_context}"}
        ]
        
        gpt_response = client.chat.completions.create(
            model="gpt-4.1",
            messages=messages
        )
        dalle_prompt = gpt_response.choices[0].message.content
        
        # Generuj obraz
        image_response = client.images.generate(
            model="dall-e-3",
            prompt=dalle_prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        
        image_url = image_response.data[0].url
        
        # Generuj szczegółowy opis obrazu
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Przygotuj mi bardzo dokładny opis postaci na obrazku. Chcę by opis dokładnie odzwierciedlał zarówno wygląd zewnętrzny jak i cechy charakteru postaci. Pamiętaj, żeby na podstawie opisu dało się dokładnie odtworzyć stylistykę pierwotnego obrazu. Chcę wykorzystywać opis do tworzenia kolejnych obrazów tej postaci podczas różnych czynności."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url
                        }
                    }
                ]
            }
        ]
        
        gpt_response = client.chat.completions.create(
            model="gpt-4.1",
            messages=messages,
            max_tokens=1000
        )
        
        brandhero_description = gpt_response.choices[0].message.content
        
        # Zapisz obraz w GridFS
        success, file_id, image_base64 = await store_image_in_gridfs(
            image_url=image_url,
            company_id=company_id,
            description=brandhero_description
        )
        
        if success and file_id:
            # Zapisz kontekst, opis i referencję do obrazu w MongoDB
            db_success = await update_brandhero_context(
                company_id=company_id,
                brandhero_context=brandhero_context,
                previous_response_id=previous_response_id,
                brandhero_description=brandhero_description,
                image_url=f"/api/images/{file_id}"  # URL do naszego endpointu
            )
            
            if not db_success:
                logger.error(f"Failed to save brand hero context for company_id={company_id}")
                return "Nie udało się zapisać kontekstu brand hero."
            
            logger.info(f"Generated and saved brand hero image and description for company_id={company_id}")
            
            # Return a detailed response with all the brand hero information
            return f"""
Brand Hero Context:
{brandhero_context}

Brand Hero Description (based on generated image):
{brandhero_description}

Image URL: /api/images/{file_id}
"""
        else:
            # Jeśli nie udało się zapisać obrazu, zapisz przynajmniej kontekst i opis z oryginalnym URL
            await update_brandhero_context(
                company_id=company_id,
                brandhero_context=brandhero_context,
                previous_response_id=previous_response_id,
                brandhero_description=brandhero_description,
                image_url=image_url  # Oryginalny URL z OpenAI
            )
            
            return f"Wygenerowano obraz brand hero, ale wystąpił błąd podczas zapisywania go w bazie danych. URL obrazu: {image_url}"
        
    except Exception as e:
        logger.exception(f"Error generating brand hero: {str(e)}")
        return f"Wystąpił błąd podczas generowania brand hero: {str(e)}"

@function_tool
async def update_brand_hero(company_id: str, updated_context: str) -> str:
    """
    Aktualizuje kontekst brand hero i regeneruje obraz na podstawie zaktualizowanego kontekstu.
    """
    try:
        # Pobierz aktualny dokument, aby zachować previous_response_id
        doc = await get_brandhero_context(company_id)
        if not doc:
            logger.error(f"No brand hero context found for company_id={company_id}")
            return "Nie znaleziono kontekstu brand hero do aktualizacji."
        
        previous_response_id = doc.get("previous_response_id")
        
        # Zapisz zaktualizowany kontekst
        success = await update_brandhero_context(
            company_id=company_id,
            brandhero_context=updated_context,
            previous_response_id=previous_response_id
        )
        
        if not success:
            logger.error(f"Failed to update brand hero context for company_id={company_id}")
            return "Nie udało się zaktualizować kontekstu brand hero."
        
        # Regeneruj obraz na podstawie zaktualizowanego kontekstu
        return await generate_brand_hero(company_id)
        
    except Exception as e:
        logger.exception(f"Error updating brand hero: {str(e)}")
        return f"Wystąpił błąd podczas aktualizacji brand hero: {str(e)}"

@function_tool
async def update_brand_hero_image(company_id: str, updated_description: str) -> str:
    """
    Aktualizuje opis brand hero i regeneruje obraz na podstawie zaktualizowanego opisu.
    """
    try:
        # Pobierz aktualny dokument
        doc = await get_brandhero_context(company_id)
        if not doc:
            logger.error(f"No brand hero context found for company_id={company_id}")
            return "Nie znaleziono kontekstu brand hero do aktualizacji."
        
        brandhero_context = doc.get("brandhero_context", "")
        previous_response_id = doc.get("previous_response_id")
        
        # Zapisz zaktualizowany opis
        success = await update_brandhero_context(
            company_id=company_id,
            brandhero_context=brandhero_context,
            previous_response_id=previous_response_id,
            brandhero_description=updated_description
        )
        
        if not success:
            logger.error(f"Failed to update brand hero description for company_id={company_id}")
            return "Nie udało się zaktualizować opisu brand hero."
        
        # Generuj nowy obraz na podstawie zaktualizowanego opisu
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Generuj obraz
        image_response = client.images.generate(
            model="dall-e-3",
            prompt=updated_description,
            size="1024x1024",
            quality="standard",
            n=1
        )
        
        image_url = image_response.data[0].url
        
        # Zapisz obraz w GridFS
        success, file_id, image_base64 = await store_image_in_gridfs(
            image_url=image_url,
            company_id=company_id,
            description=updated_description
        )
        
        if success and file_id:
            # Zaktualizuj referencję do obrazu w MongoDB
            db_success = await update_brandhero_context(
                company_id=company_id,
                brandhero_context=brandhero_context,
                previous_response_id=previous_response_id,
                brandhero_description=updated_description,
                image_url=f"/api/images/{file_id}"  # URL do naszego endpointu
            )
            
            if not db_success:
                logger.error(f"Failed to update brand hero image reference for company_id={company_id}")
                return "Nie udało się zaktualizować referencji do obrazu brand hero."
            
            logger.info(f"Updated brand hero image for company_id={company_id}")
            
            # Return a detailed response with all the brand hero information
            return f"""
Brand Hero Context:
{brandhero_context}

Brand Hero Description (updated):
{updated_description}

Image URL: /api/images/{file_id}
"""
        else:
            return f"Wygenerowano nowy obraz brand hero, ale wystąpił błąd podczas zapisywania go w bazie danych."
        
    except Exception as e:
        logger.exception(f"Error updating brand hero image: {str(e)}")
        return f"Wystąpił błąd podczas aktualizacji obrazu brand hero: {str(e)}"

@function_tool
async def get_company_context_data(company_id: str) -> str:
    """
    Pobiera kontekst firmy z bazy MongoDB.
    """
    try:
        # Pobierz kontekst firmy z MongoDB
        doc = await get_company_context(company_id)
        
        # Jeśli dokument nie istnieje, zwróć informację o braku danych
        if not doc:
            logger.warning(f"Company context for company_id={company_id} not found")
            return "Brak danych kontekstowych dla firmy."
        
        # Zwróć context_description
        return doc["context_description"]
    except Exception as e:
        logger.error(f"Error retrieving company context from MongoDB: {str(e)}")
        return "Wystąpił błąd podczas pobierania kontekstu firmy."

async def dynamic_instructions(wrapper, agent) -> str:
    cid = wrapper.context['company_id']
    return get_brand_hero_prompt(cid)

class BranHeroContextAgent:
    def __init__(self):
        logger.info("Initializing BrandHeroContextAgent")
        self.agent = Agent(
            name="BHContextCollector",
            instructions=dynamic_instructions,
            model="o4-mini",
            tools=[
                store_context, 
                get_company_context_data, 
                generate_brand_hero,
                update_brand_hero,
                update_brand_hero_image
            ],
            model_settings=ModelSettings(tool_choice="auto"),  # pozwól LLM decydować
        )

    async def run(self, company_id: str, user_response: Optional[str] = None) -> Dict[str, Any]:
        """
        Uruchamia agenta zbierającego kontekst brand hero.

        Args:
            company_id: Identyfikator firmy
            user_response: Opcjonalna odpowiedź użytkownika na pytanie agenta

        Returns:
            Słownik zawierający wynik działania agenta i identyfikator ostatniej odpowiedzi
        """
        # 1. Zbuduj kontekst dla agenta
        context = {"company_id": company_id}

        # 2. Pobierz poprzedni identyfikator odpowiedzi z MongoDB
        doc = await get_brandhero_context(company_id)
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
            # Pobierz aktualny kontekst brand hero, jeśli istnieje
            doc = await get_brandhero_context(company_id)
            brandhero_context = doc.get("brandhero_context", "") if doc else ""
            
            # Aktualizuj dokument z nowym previous_response_id
            await update_brandhero_context(
                company_id=company_id,
                brandhero_context=brandhero_context,
                previous_response_id=last_response_id
            )
            logger.info(f"Updated previous_response_id for company {company_id}")

        return {
            "output": getattr(result, 'final_output', None),
            "previous_response_id": last_response_id
        }

# Inicjalizacja agenta dla importu w api.py
agent_instance = BranHeroContextAgent()
agent = agent_instance.agent
runner = Runner()

# Funkcja opakowująca dla zachowania kompatybilności z istniejącym kodem
async def run_bh_agent(agent, company_id, user_response=None):
    """
    Funkcja opakowująca dla zachowania kompatybilności z istniejącym kodem.
    """
    return await agent_instance.run(company_id, user_response)
