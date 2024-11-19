import sqlite3
from datetime import datetime

# Adapter to convert datetime to a string for storage
def adapt_datetime(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")

# Converter to parse string back into a datetime object
def convert_datetime(s):
    return datetime.strptime(s.decode("utf-8"), "%Y-%m-%d %H:%M:%S")

# Register adapters and converters
sqlite3.register_adapter(datetime, adapt_datetime)
sqlite3.register_converter("DATETIME", convert_datetime)

def initialize_database(db_path="food_consumption.db"):
    """
    Initializes the database with the required schema if it doesn't already exist.
    """
    conn = sqlite3.connect(
        db_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
    )
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS FoodConsumption (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            food_name TEXT,
            quantity INTEGER,
            time_eaten DATETIME,
            calories INTEGER,
            protein FLOAT,
            carbs FLOAT,
            fats FLOAT
        )
    """)
    conn.commit()
    conn.close()
