import pinecone
from dotenv import load_dotenv
import os
from openai import OpenAI
from pinecone import Pinecone
import json

load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
#PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
client = OpenAI()

# Initialize Pinecone
def initialize_pinecone():
    """
    Initialize Pinecone client and ensure the index exists.
    """
    pc = Pinecone(api_key=PINECONE_API_KEY)
    return pc.Index("munchhunch")  # Replace with your actual index name

# Function to generate embeddings and upsert into Pinecone
def add_to_pinecone(macros, index):
    """
    Generates embeddings for the macro entry and adds it to the Pinecone index.
    """
    # Creating a vector embedding using a simplified string representation of the entry
    vector_data = f"{macros['Item']}, {macros['Quantity']}, Calories: {macros['Calories']}, Protein: {macros['Protein']}, Carbs: {macros['Carbs']}, Fats: {macros['Fats']}, Fiber: {macros['Fiber']}"
    
    # Assuming OpenAI embeddings for demonstration
    embedding = client.embeddings.create(
        input=json.dumps(macros),
        model="text-embedding-3-large"
    )
    vector = embedding.data[0].embedding

    # Upsert into Pinecone
    index.upsert([
        {
            "id": str(macros["Item"] + "-" + macros["Time Eaten"]),
            "values": vector,
            "metadata": {
                "item": macros["Item"],
                "quantity": macros["Quantity"],
                "calories": macros["Calories"],
                "protein": macros["Protein"],
                "carbs": macros["Carbs"],
                "fats": macros["Fats"],
                "fiber": macros["Fiber"],
                "time_eaten": macros["Time Eaten"]
            }
        }
    ])
    print(f"Added {macros['Item']} to Pinecone index.")