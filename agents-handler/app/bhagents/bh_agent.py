from agents import Agent, Runner, function_tool, ModelSettings
from typing import Optional, Dict, Any
from pymongo import MongoClient
import os
import logging
import datetime
from app.bhagents.prompts import get_brand_hero_prompt
from openai import OpenAI
logger = logging.getLogger(__name__)

# MongoDB setup
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
mongo_client = MongoClient(MONGODB_URI)
mongo_db = mongo_client[os.getenv("MONGODB_DB", "brand-hero")]
bh_context_collection = mongo_db["bh_context_memory"]
company_context_collection = mongo_db["company_context_memory"]

@function_tool
async def store_context(company_id: str, context_description: str) -> None:
    try:
        # Pobierz aktualny dokument, aby zachować previous_response_id
        doc = bh_context_collection.find_one({"company_id": company_id})
        previous_response_id = doc.get("previous_response_id") if doc else None

        # Aktualizacja lub utworzenie dokumentu z kontekstem firmy
        bh_context_collection.update_one(
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

@function_tool
async def generate_brand_hero(company_id: str) -> None:
    """
    Generuje obraz brand hero i zapisuje go w bazie
    """
    try:


        # Pobierz aktualny dokument, aby zachować previous_response_id
        doc = bh_context_collection.find_one({"company_id": company_id})
        previous_response_id = doc.get("description") if doc else None


        client = OpenAI()
        messages=[
            {"role": "system", "content": "Jesteś pomocnikiem tworzącym wysokiej jakości prompty do DALL·E 3. Ulepszaj opisy postaci, dodając szczegóły dotyczące wyglądu, emocji, otoczenia, kompozycji i stylu graficznego."},
            {"role": "system", "content":"A brand hero is a personification of a brand – a character (real or fictional) that represents the brand’s values, personality, and way of communicating with its audience. The brand hero acts as the 'face of the brand' and can appear in advertisements,"
                                     " on packaging, websites, and social media. Its main goal is to build emotional connections with customers, strengthen brand recognition, and make the brand stand out from the competition."},
            {"role": "system", "content":"Good brand hero should be simple. Should be easy to use in all forms of advertisements."},
            {"role": "system", "content":"Reduce details."},
            {"role": "system", "content": f"Generate detailed prompt do DALL·E to generate image of brand hero of described: {doc.context_description}"}
        ]

        gpt_response = client.chat.completions.create(
            model="gpt-4.1",
            messages=messages
        )
        dalle_prompt = gpt_response.choices[0].message.content
        image_response = client.images.generate(
            model="dall-e-3",
            prompt=dalle_prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )

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
            image_url=image_response.data[0].url,
            contextId=company_id,
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

@function_tool
async def get_company_context(company_id: str) -> str:
    return "Firma ASD-230 zajmuje się dostarczaniem pizzy. Misją firmy jest dostarczać pizzę i być najszybszymi dostawcami na rynku. Wizją firmy jest stać się rozpoznawalną marką oferującą najszybszy dowóz pizzy. Kluczowe wartości to szybkość i dokładność. Firma działa obecnie w Warszawie, w dzielnicy Wawer, a w planach ma rozszerzenie działalności na Warszawę Wesołą. Kultura organizacyjna opiera się na skupieniu na wydajności i dobrej organizacji pracy, co tworzy atmosferę efektywnej i dobrze zorganizowanej współpracy zespołowej."

async def dynamic_instructions(wrapper, agent) -> str:
    cid = wrapper.context['company_id']
    return get_brand_hero_prompt(cid)

class BranHeroContextAgent:
    def __init__(self):
        logger.info("Initializing CompanyContextAgent")
        self.agent = Agent(
            name="BHContextCollector",
            instructions=dynamic_instructions,
            model="o4-mini",
            tools=[store_context, get_company_context, generate_brand_hero],
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
        doc = bh_context_collection.find_one({"company_id": company_id})
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
            bh_context_collection.update_one(
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
agent_instance = BranHeroContextAgent()
agent = agent_instance.agent
runner = Runner()

# Funkcja opakowująca dla zachowania kompatybilności z istniejącym kodem
async def run_bh_agent(agent, company_id, user_response=None):
    """
    Funkcja opakowująca dla zachowania kompatybilności z istniejącym kodem.
    """
    return await agent_instance.run(company_id, user_response)
