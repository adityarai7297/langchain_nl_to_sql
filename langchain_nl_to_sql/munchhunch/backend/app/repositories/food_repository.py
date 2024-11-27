from sqlalchemy.orm import Session
from app.models.food_entry import FoodEntryDB
from sqlalchemy import select
from datetime import datetime

class FoodRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all_entries(self):
        stmt = select(FoodEntryDB)
        result = self.db.execute(stmt)
        return result.scalars().all()
    
    async def add_entry(self, entry_data: dict):
        """Add a new food entry to the database."""
        try:
            # Parse the time string into a datetime object
            time_eaten = datetime.strptime(entry_data['Time Eaten'], '%H:%M %p, %d, %b, %Y')
            
            food_entry = FoodEntryDB(
                item=entry_data['Item'],
                quantity=str(entry_data['Quantity']),
                time_eaten=time_eaten,
                calories=entry_data['Calories'],
                protein=entry_data['Protein'],
                carbs=entry_data['Carbs'],
                fats=entry_data['Fats'],
                fiber=entry_data['Fiber']
            )
            
            self.db.add(food_entry)
            self.db.commit()
            self.db.refresh(food_entry)
            
            return food_entry
            
        except Exception as e:
            self.db.rollback()
            raise
    
    # class implementation
    pass
