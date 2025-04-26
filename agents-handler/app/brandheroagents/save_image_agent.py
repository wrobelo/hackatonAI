import logging
import openai
import json
from typing import Dict
from agents import Agent, Runner, function_tool
from openai import OpenAI
import requests
import gridfs
from pymongo import MongoClient
import datetime
from bson.objectid import ObjectId
from app.schemas import SaveImage
import os
import gridfs
from pymongo import MongoClient
from bson.objectid import ObjectId
from fastapi.responses import StreamingResponse
import io

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
mongo_client = MongoClient(MONGODB_URI)
mongo_db_name="brand-hero"
mongo_db = mongo_client[os.getenv("MONGODB_DB", mongo_db_name)]
collection_name="images"
client = MongoClient(MONGODB_URI)
db = client[mongo_db_name]
fs = gridfs.GridFS(db)

class SaveImageAgent:
    async def run(self, req: SaveImage) -> str:
        logger.info("Starting image saving for: %s", req)
        try:
            download_and_save_to_mongodb(req)
            return "ok"

        except Exception as e:
            logger.exception("Error in image generation", e)
            raise

    def retrieve_image_from_mongodb(file_id):
        try:
            try:
                grid_out = fs.get(ObjectId(file_id))
                # Get content type from metadata if available
                content_type = None
                if hasattr(grid_out, 'metadata') and grid_out.metadata and 'content_type' in grid_out.metadata:
                    content_type = grid_out.metadata['content_type']
                else:
                    content_type = 'image/jpeg'
                return grid_out.read(), content_type

            except gridfs.errors.NoFile:
                print(f"No file found with ID: {file_id}")
                return None, None

        except Exception as e:
            print(f"Error retrieving image from MongoDB: {e}")
            return None, None

def download_and_save_to_mongodb(req: SaveImage):
    try:
        # Extract URL from the generate result
        image_url = req.image_url

        if not image_url:
            print("No URL found in the generate result")
            return None
        response = requests.get(image_url, stream=True)
        response.raise_for_status()  # Raise exception for HTTP errors

        # Prepare metadata
        metadata = {
            "source_url": image_url,
            "date_created": datetime.datetime.now(),
            "content_type": response.headers.get('Content-Type', 'image/jpeg'),
        }

        filename = image_url.split('/')[-1] if '/' in image_url else "brand_hero_image.jpg"
        client = MongoClient(MONGODB_URI)
        db = client[mongo_db_name]
        fs = gridfs.GridFS(db)
        file_id = fs.put(
            response.content,
            filename=req.contextId,
            metadata=metadata
        )
        db[collection_name].insert_one({
            "file_id": file_id,
            "filename": filename,
            "metadata": metadata,
            "date_saved": datetime.datetime.now(),
            "description": req.description
        })

        return None

    except Exception as e:
        print(f"Error saving image to MongoDB: {e}")
        return None

