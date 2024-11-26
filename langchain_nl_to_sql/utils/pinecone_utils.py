from typing import Dict, Any
import os
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone, Index
import json

load_dotenv()

class PineconeClient:
    """Handles interactions with Pinecone vector database."""
    
    def __init__(self):
        self.api_key = os.getenv("PINECONE_API_KEY")
        if not self.api_key:
            raise ValueError("PINECONE_API_KEY environment variable not set")
        self.client = OpenAI()
        
    def initialize_index(self, index_name: str = "munchhunch") -> Index:
        """
        Initialize Pinecone index.
        
        Args:
            index_name (str): Name of the Pinecone index
            
        Returns:
            Index: Initialized Pinecone index
        """
        pc = Pinecone(api_key=self.api_key)
        return pc.Index(index_name)
        
    def add_entry(self, macros: Dict[str, Any], index: Index) -> None:
        """
        Add food entry to Pinecone index.
        
        Args:
            macros (Dict[str, Any]): Macronutrient data to store
            index (Index): Pinecone index instance
        """
        try:
            vector_data = self._create_vector_data(macros)
            embedding = self._generate_embedding(macros)
            
            index.upsert([{
                "id": f"{macros['Item']}-{macros['Time Eaten']}",
                "values": embedding,
                "metadata": vector_data
            }])
            
        except Exception as e:
            raise RuntimeError(f"Failed to add entry to Pinecone: {str(e)}")