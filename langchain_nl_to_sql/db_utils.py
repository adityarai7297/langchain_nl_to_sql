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
            fats FLOAT,
            fiber FLOAT
        )
    """)
    conn.commit()
    conn.close()
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
