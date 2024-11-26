import re
import json
import sqlite3
from datetime import datetime, timedelta
from db_utils import initialize_database, update_database_schema, print_all_entries, print_total_calories
from openai import OpenAI
from pinecone_utils import initialize_pinecone, add_to_pinecone
initialize_database()
#update_database_schema()
client = OpenAI()

# JSON extraction function
def extract_json(gpt_response):
    """
    Extracts a JSON object from a GPT response, ignoring any extra text or comments.
    """
    try:
        json_match = re.search(r'\{.*\}', gpt_response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())  # Parse and return the JSON
        else:
            raise ValueError("No valid JSON object found in GPT response.")
    except json.JSONDecodeError as e:
        raise ValueError(f"Error decoding JSON: {e}")


# Agent 1: Parsing Natural Language
def agent_1(user_input):
    """
    Parses natural language input into structured JSON format.
    Handles multiple items.
    """
    prompt = f"""
    You are an assistant that parses natural language inputs about food consumption into valid JSON format.
    - Parse multiple distinct food items from the input and separate them into a list of JSON objects.
    - Each item should have its own JSON object.
    - Ensure that combinations like 'Diet Coke and Naan' are separated as distinct entries.
    - Always output a valid JSON array with no additional text, comments, or explanations.
    - Use double quotes (" ") for all keys and string values.
    - The 'Time Eaten' field should be in the format "HH:MM AM, DD, MMM, YYYY".
    - If no time is mentioned,use CURRENT TIME = {datetime.now().strftime("%H:%M %p, %d, %b, %Y")}".
    - If yesterday morning, today evening, and other unclear times are mentioned, intelligently infer the time in the format "HH:MM AM, DD, MMM, YYYY" using CURRENT TIME as reference.
    - Ensure all timestamps are normalized and resolved.


    Example Input: "I had two Diet Cokes and a bowl of carrots this morning."
    Example Output:
    [
        {{
            "Task": "Add",
            "Item": "Diet Coke",
            "Quantity": "2 cans",
            "Time Eaten": "HH:MM AM, DD, MMM, YYYY"
        }},
        {{
            "Task": "Add",
            "Item": "Carrots",
            "Quantity": "1 bowl",
            "Time Eaten": "HH:MM AM, DD, MMM, YYYY"
        }}
    ]

    Parse this input: "{user_input}"
    """
  
    print("------------------> Agent 1 Request: Parsing", user_input)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant for parsing natural language into JSON."},
            {"role": "user", "content": prompt},
        ],
        temperature=0
    )
    
    # Clean the response by removing any markdown formatting
    cleaned_response = response.choices[0].message.content.strip()
    cleaned_response = re.sub(r'^```json\s*|\s*```$', '', cleaned_response)
    
    # Check for missing information
    parsed_json_list = json.loads(cleaned_response)
    for entry in parsed_json_list:
        if not entry.get("Item") or not entry.get("Quantity") or not entry.get("Time Eaten"):
            # Ask for clarification
            clarification_needed = []
            if not entry.get("Item"):
                clarification_needed.append("item name")
            if not entry.get("Quantity"):
                clarification_needed.append("quantity")
            if not entry.get("Time Eaten"):
                clarification_needed.append("time eaten")
            
            clarification_prompt = f"Could you please clarify the {', '.join(clarification_needed)} for '{user_input}'?"
            print(clarification_prompt)
            # Here you would implement a way to get the user's response and update the entry accordingly
            # For example, using a simple input() call or a GUI dialog

    print("------------------> Agent 1 Response: Parsed JSON", cleaned_response)
    return parsed_json_list

# Agent 2: Calculate Macros
def agent_2(parsed_json):
    """
    Calculates macros for the given item and quantity directly.
    """
    item_name = parsed_json["Item"]
    quantity = parsed_json["Quantity"]
    print("------------------> Agent 2 Request: finding macros for", item_name, quantity)
    prompt = f"""
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
        "Time Eaten": "{parsed_json['Time Eaten']}"
    }}
    Do not output anything else. Ensure the JSON is valid.
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant for calculating nutritional macros."},
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )
    print("------------------> Agent 2 Response: Macros ", response.choices[0].message.content.strip())
    return extract_json(response.choices[0].message.content.strip())

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
    parsed_json_list = agent_1(user_input)
    pinecone_index = initialize_pinecone()

    for parsed_json in parsed_json_list:
        macros = agent_2(parsed_json)
        add_to_pinecone(macros, pinecone_index)
        store_in_database(macros)

    print_all_entries()  # Display all entries after processing


# Main Function
if __name__ == "__main__":
    import tkinter as tk
    from tkinter import simpledialog

    # Create and hide the root window
    root = tk.Tk()
    root.withdraw()

    # Initialize database
    initialize_database()
    
    while True:
        # Show input dialog
        user_input = simpledialog.askstring("Food Entry", "What did you eat?")
        
        # Break the loop if user cancels or closes the dialog
        if user_input is None:
            break
            
        process_user_input(user_input)
    
    root.destroy()