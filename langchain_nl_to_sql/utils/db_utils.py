from typing import List, Dict, Any, Optional
import sqlite3
from datetime import datetime
from contextlib import contextmanager
from pathlib import Path

@contextmanager
def get_db_connection(db_path: str = "food_consumption.db"):
    """
    Context manager for database connections.
    
    Args:
        db_path (str): Path to SQLite database file
    """
    conn = sqlite3.connect(
        db_path,
        detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
    )
    try:
        yield conn
    finally:
        conn.close()

def initialize_database(db_path: str = "food_consumption.db") -> None:
    """
    Initialize the database with required schema.
    
    Args:
        db_path (str): Path to SQLite database file
    """
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS FoodConsumption (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item TEXT NOT NULL,
                quantity FLOAT NOT NULL,
                time_eaten DATETIME NOT NULL,
                calories INTEGER NOT NULL,
                protein FLOAT NOT NULL,
                carbs FLOAT NOT NULL,
                fats FLOAT NOT NULL,
                fiber FLOAT DEFAULT 0
            )
        """)
        conn.commit()

def update_database_schema():
    conn = sqlite3.connect("food_consumption.db")
    cursor = conn.cursor()

    # Backup existing data
    cursor.execute("SELECT * FROM FoodConsumption")
    rows = cursor.fetchall()

    # Drop the old table
    cursor.execute("DROP TABLE IF EXISTS FoodConsumption")

    # Create the new table with the "fiber" column
    cursor.execute("""
        CREATE TABLE FoodConsumption (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item TEXT,
            quantity FLOAT,
            time_eaten DATETIME,
            calories INTEGER,
            protein FLOAT,
            carbs FLOAT,
            fats FLOAT,
            fiber FLOAT DEFAULT 0
        )
    """)

    # Reinsert the data, setting fiber to a default value (e.g., 0)
    for row in rows:
        cursor.execute("""
            INSERT INTO FoodConsumption (id, item, quantity, time_eaten, calories, protein, carbs, fats, fiber)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, row + (0,))  # Append default value for fiber

    conn.commit()
    conn.close()
def print_all_entries():
    """
    Fetches and prints all entries from the FoodConsumption table.
    """
    import sqlite3

    conn = sqlite3.connect("food_consumption.db")
    cursor = conn.cursor()

    try:
        # Fetch all entries from the FoodConsumption table
        cursor.execute("SELECT * FROM FoodConsumption")
        rows = cursor.fetchall()

        # Fetch column names for better formatting
        cursor.execute("PRAGMA table_info(FoodConsumption)")
        columns = [column[1] for column in cursor.fetchall()]

        # Print column names
        print(f"{' | '.join(columns)}")
        print("-" * 80)

        # Print each row
        for row in rows:
            print(" | ".join(str(value) for value in row))

    except sqlite3.Error as e:
        print(f"Error fetching data: {e}")
    finally:
        conn.close()

def print_total_calories():
   
    import sqlite3

    conn = sqlite3.connect("food_consumption.db")
    cursor = conn.cursor()

    try:
        # Fetch all entries from the FoodConsumption table
        cursor.execute("SELECT SUM(calories) FROM FoodConsumption")
        total_calories = cursor.fetchone()[0]
        print(f"Total calories consumed: {total_calories}")

    except sqlite3.Error as e:
        print(f"Error fetching data: {e}")
    finally:
        conn.close()

def store_in_database(macros, db_path="food_consumption.db"):
    """
    Stores the validated macros in the SQLite database.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO FoodConsumption 
            (item, quantity, time_eaten, calories, protein, carbs, fats, fiber)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            macros["Item"],
            macros["Quantity"],
            macros["Time Eaten"],
            macros["Calories"],
            macros["Protein"],
            macros["Carbs"],
            macros["Fats"],
            macros["Fiber"]
        ))
        conn.commit()
        print(f"Stored {macros['Item']} in database.")
    except sqlite3.Error as e:
        print(f"Error storing in database: {e}")
    finally:
        conn.close()