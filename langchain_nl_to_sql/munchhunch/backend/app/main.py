from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from .models.food_entry import FoodEntry, MacroResponse
from .services.agent_service import AgentService
from .repositories.food_repository import FoodRepository
from .config import get_db
from app.utils.db_utils import initialize_database
from .api.endpoints import speech
import traceback
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(title="MunchHunch API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add this near the start of your application, before creating the FastAPI app
initialize_database()

app.include_router(
    speech.router,
    prefix="/api/v1",
    tags=["speech"]
)

@app.post("/api/food-entries", response_model=List[MacroResponse])
async def create_food_entry(
    entry: FoodEntry,
    db: Session = Depends(get_db),
    agent_service: AgentService = Depends(AgentService),
):
    """Process natural language food entry and store results."""
    try:
        logger.debug(f"Processing input text: {entry.input_text}")
        results = await agent_service.process_user_input(entry.input_text)
        logger.debug(f"Agent service results: {results}")
        
        repo = FoodRepository(db)
        stored_entries = []
        
        for result in results:
            logger.debug(f"Storing entry: {result}")
            stored_entry = await repo.add_entry(result)
            stored_entries.append(MacroResponse.from_orm(stored_entry))
            
        return stored_entries
    except Exception as e:
        logger.error(f"Error processing food entry: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/food-entries", response_model=List[MacroResponse])
async def get_food_entries(
    db: Session = Depends(get_db)
):
    """Retrieve all food entries."""
    repo = FoodRepository(db)
    entries = repo.get_all_entries()
    return [MacroResponse.from_orm(entry) for entry in entries]