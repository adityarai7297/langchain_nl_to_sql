from typing import Dict, Any, List
import os
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone, Index
import logging
import traceback 

load_dotenv()

logger = logging.getLogger(__name__)

class PineconeService:
    def __init__(self, settings=None):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        self.client = OpenAI(api_key=self.openai_api_key)

        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        if not self.pinecone_api_key:
            raise ValueError("PINECONE_API_KEY not found in environment variables")

    def initialize_index(self, index_name: str = "munchhunch") -> Index:
        """Initialize Pinecone index."""
        pc = Pinecone(api_key=self.pinecone_api_key)
        return pc.Index(index_name)
        
    async def add_entry(self, macros: Dict[str, Any], index: Index) -> None:
        """Add food entry to vector database."""
        try:
            logger.debug(f"Generating embedding for macros: {macros}")
            embedding = await self._generate_embedding(macros)
            
            logger.debug("Attempting to upsert to Pinecone")
            vector_data = {
                "id": f"{macros['Item']}-{macros['Time Eaten']}",
                "values": embedding,
                "metadata": macros
            }
            logger.debug(f"Upserting vector data: {vector_data}")
            
            index.upsert([vector_data])
            logger.debug("Successfully upserted to Pinecone")
            
        except Exception as e:
            logger.error(f"Failed to add entry to Pinecone: {str(e)}")
            logger.error(traceback.format_exc())
            raise RuntimeError(f"Failed to add entry to Pinecone: {str(e)}")
            
    async def _generate_embedding(self, macros: Dict[str, Any]) -> List[float]:
        """Generate embedding for food entry."""
        try:
            text = f"{macros['Item']} {macros.get('Quantity', '')} {macros.get('Time Eaten', '')}"
            response = self.client.embeddings.create(
                model="text-embedding-3-large",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {str(e)}")
            logger.error(traceback.format_exc())
            raise
