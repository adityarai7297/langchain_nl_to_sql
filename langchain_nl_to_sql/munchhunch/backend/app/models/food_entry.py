from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class FoodEntryDB(Base):
    __tablename__ = "food_consumption"
    
    id = Column(Integer, primary_key=True, index=True)
    item = Column(String, nullable=False)
    quantity = Column(String, nullable=False)  # Changed from Float to String
    time_eaten = Column(DateTime, nullable=False)
    calories = Column(Integer, nullable=False)
    protein = Column(Float, nullable=False)
    carbs = Column(Float, nullable=False)
    fats = Column(Float, nullable=False)
    fiber = Column(Float, nullable=False, default=0)

class FoodEntry(BaseModel):
    input_text: str

class MacroResponse(BaseModel):
    id: Optional[int]
    item: str
    quantity: str
    time_eaten: datetime
    calories: int
    protein: float
    carbs: float
    fats: float
    fiber: float

    model_config = ConfigDict(from_attributes=True)
