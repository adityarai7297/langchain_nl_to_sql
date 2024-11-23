import re
import json
import sqlite3
from datetime import datetime, timedelta
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from db_utils import initialize_database, update_database_schema, print_all_entries, print_total_calories

initialize_database()

llm = ChatOpenAI(model="gpt-4", temperature=0)

# JSON extraction function
def extract_json(response_text):
    """
    Extracts a JSON object from a GPT response, ignoring any extra text or comments.
    """
    try:
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())  # Parse and return the JSON
        else:
            raise ValueError("No valid JSON object found in response.")
    except json.JSONDecodeError as e:
        raise ValueError(f"Error decoding JSON: {e}")

def resolve_dynamic_dates(timestamp):
    """
    Replace placeholders like 'Today' or 'Yesterday' in timestamps with actual dates.
    """
    current_date = datetime.now()
    if "Today" in timestamp:
        timestamp = timestamp.replace("Today", current_date.strftime("%A, %b %d, %Y"))
    elif "Yesterday" in timestamp:
        yesterday_date = current_date - timedelta(days=1)
        timestamp = timestamp.replace("Yesterday", yesterday_date.strftime("%A, %b %d, %Y"))
    return timestamp

def normalize_day_name(timestamp):
    """
    Expands abbreviated day names in a timestamp to full names.
    """
    day_abbrev_to_full = {
        "Mon": "Monday",
        "Tue": "Tuesday",
        "Wed": "Wednesday",
        "Thu": "Thursday",
        "Fri": "Friday",
        "Sat": "Saturday",
        "Sun": "Sunday",
    }

    for abbrev, full in day_abbrev_to_full.items():
        if f"{abbrev}," in timestamp or f"{abbrev} " in timestamp:
            return timestamp.replace(abbrev, full)
    return timestamp

def validate_and_format_time(time_eaten):
    """
    Validates and reformats the 'Time Eaten' field to match the desired format.
    """
    if time_eaten.strip().lower() == "current time":
        return datetime.now().strftime("%I:%M %p, %A, %b %d, %Y")

    try:
        return datetime.strptime(time_eaten, "%I:%M %p, %A, %b %d, %Y").strftime("%I:%M %p, %A, %b %d, %Y")
    except ValueError:
        return datetime.now().strftime("%I:%M %p, %A, %b %d, %Y")

# Agent 1: Parsing Natural Language
parse_prompt = PromptTemplate(
    input_variables=["user_input"],
    template="""You are an assistant that parses natural language inputs about food consumption into valid JSON format.
    - Parse multiple distinct food items from the input and separate them into a list of JSON objects.
    - Each item should have its own JSON object with exactly these keys: "Item", "Quantity", "Time Eaten"
    - Ensure that combinations like 'Diet Coke and Naan' are separated as distinct entries.
    - Always output a valid JSON array with no additional text, comments, or explanations.
    - Use double quotes (" ") for all keys and string values.
    - If no quantity is specified, use "1 serving" as the default.
    - Ensure all timestamps are normalized and resolved.

    Example output format:
    [
        {
            "Item": "butter chicken",
            "Quantity": "1 serving",
            "Time Eaten": "current time"
        }
    ]

    Handle ambiguous times as follows:
    - If the input mentions 'this morning', assume today at 8:00 AM.
    - If the input mentions 'yesterday', assume the previous day at 12:00 PM.
    - If the input mentions 'tonight', assume today at 8:00 PM.
    - If the input mentions 'at breakfast', 'at lunch', or 'after dinner', infer times dynamically:
        - Breakfast: 8:00 AM.
        - Lunch: 1:00 PM.
        - Dinner: 8:00 PM.
    - If no time is mentioned, default to the current time in the format "HH:MM AM/PM, Day, Month DD, YYYY".

    Parse this input: {user_input}"""
)

parse_chain = parse_prompt | llm

# Agent 2: Calculate Macros
macro_prompt = PromptTemplate(
    input_variables=["item_name", "quantity", "time_eaten"],
    template="""
    You are a nutritional assistant that calculates the macros for food items.
    For the item '{item_name}' and the quantity '{quantity}', provide the following JSON:
    {{
        "Item": "{item_name}",
        "Quantity": "{quantity}",
        "Calories": <integer>,  # Total calories for the quantity specified
        "Protein": <float>,  # Total protein in grams
        "Carbs": <float>,  # Total carbohydrates in grams
        "Fats": <float>,  # Total fats in grams
        "Fiber": <float>,  # Total fiber in grams
        "Time Eaten": "{time_eaten}"
    }}
    Do not output anything else. Ensure the JSON is valid.
    """
)

macro_chain = LLMChain(llm=llm, prompt=macro_prompt)

# Database Execution
def store_in_database(macros):
    """
    Stores each distinct calculated macro entry into the FoodConsumption database table.
    """
    conn = sqlite3.connect("food_consumption.db")
    cursor = conn.cursor()

    # Ensure the table exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS FoodConsumption (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item TEXT,
        quantity TEXT,
        calories INTEGER,
        protein REAL,
        carbs REAL,
        fats REAL,
        fiber REAL,
        time_eaten TEXT
    )
    """)

    # Insert a new entry for each distinct item
    cursor.execute(
        """
        INSERT INTO FoodConsumption (item, quantity, calories, protein, carbs, fats, fiber, time_eaten)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            macros["Item"],
            macros["Quantity"],
            macros["Calories"],
            macros["Protein"],
            macros["Carbs"],
            macros["Fats"],
            macros["Fiber"],
            macros["Time Eaten"]
        )
    )
    print(f"Added new entry for item: {macros['Item']}")

    conn.commit()
    conn.close()

# Orchestrator: Process User Input
def process_user_input(user_input):
    """
    Orchestrates the agents for multiple distinct items.
    """
    parsed_json_list = json.loads(parse_chain.invoke({"user_input": user_input}).content)
    print("------------------> Parsed JSON List:", parsed_json_list)

    for parsed_json in parsed_json_list:
        item_name = parsed_json["Item"]
        quantity = parsed_json["Quantity"]
        time_eaten = resolve_dynamic_dates(parsed_json["Time Eaten"])
        time_eaten = normalize_day_name(time_eaten)
        time_eaten = validate_and_format_time(time_eaten)

        macros = extract_json(macro_chain.run(
            item_name=item_name,
            quantity=quantity,
            time_eaten=time_eaten
        ))

        # Store each item as a distinct entry
        store_in_database(macros)

    print_all_entries()  # Display all entries after processing
    print_total_calories()

# Main Function
if __name__ == "__main__":
    initialize_database()
    
    user_input = input("Hello, what did you eat? : ")
    process_user_input(user_input)