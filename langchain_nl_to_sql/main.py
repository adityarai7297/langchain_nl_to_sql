import re
import json
from datetime import datetime, timedelta
from db_utils import initialize_database
from openai import OpenAI
import sqlite3

initialize_database()
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

from datetime import datetime, timedelta

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
    Avoids overwriting already full day names.
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

    # Replace abbreviations only if they are standalone words (not part of another word)
    for abbrev, full in day_abbrev_to_full.items():
        if f"{abbrev}," in timestamp or f"{abbrev} " in timestamp:
            return timestamp.replace(abbrev, full)
    return timestamp
 # Return unchanged if no abbreviation is found

def normalize_month_name(timestamp):
    """
    Normalizes full month names to abbreviated names in a timestamp string.
    """
    from datetime import datetime
    import calendar

    # Map full month names to abbreviated names
    full_to_abbrev = {month: month[:3] for month in calendar.month_name if month}

    # Replace full month names with abbreviated ones
    for full_month, abbrev_month in full_to_abbrev.items():
        if full_month in timestamp:
            return timestamp.replace(full_month, abbrev_month)

    return timestamp  # Return the original timestamp if no change is needed


# Agent 1: Parsing Natural Language
def agent_1(user_input):
    """
    Parses natural language input into structured JSON format.
    Handles ambiguous quantities and times dynamically.
    """
    prompt = f"""
    You are an assistant that parses natural language inputs about food consumption into strictly formatted JSON.
    Your output must follow these rules:
    - Only output a valid JSON object—do not include any introductory text, explanations, or comments.
    - Use double quotes (" ") for all keys and string values.
    - Ensure the JSON object is valid and free from trailing commas or extra characters.

    For ambiguous quantities like 'a handful' or 'about a cup', infer the approximate numeric quantity dynamically based on the food item mentioned.
    For ambiguous times like 'this morning', 'yesterday', 'after dinner', or 'at breakfast':
        - 'this morning': Assume today with a default time of 8:00 AM.
        - 'yesterday': Assume the previous day at 12:00 PM (noon).
        - 'after dinner': Assume today with a default time of 8:00 PM.
        - 'at breakfast': Assume today with a default time of 8:00 AM.
        - If no time is mentioned, use the current time.

    Example Input 1: "I ate a handful of almonds this morning."
    Example Output 1:
    {{
        "Task": "Add",
        "Item": "Almonds",
        "Quantity": 28,
        "Time Eaten": "08:00 AM, Monday, Nov 18, 2024"
    }}

    Parse this input: "{user_input}"
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant for parsing natural language."},
            {"role": "user", "content": prompt},
        ],
        temperature=0
    )

    # Debugging: Print raw GPT response
    raw_response = response.choices[0].message.content.strip()
    print("Raw GPT Response:", raw_response)

    # Extract and parse JSON
    return extract_json(raw_response)

def agent_2(parsed_json):
    """
    Estimates macros and serving size for the food item using the food name.
    """
    item_name = parsed_json["Item"]

    # Simulated vector store lookup
    vector_store = {
        "Almonds": {
            "Calories": 162,
            "Protein": 6,
            "Carbs": 6,
            "Fats": 14,
            "Serving Size": 28  # Grams per serving
        }
    }

    if item_name in vector_store:
        return vector_store[item_name]

    # If not found, use GPT to estimate macros and serving size
    prompt = f"""
    You are a nutritional assistant that estimates macros and serving size for food items.
    For the item '{item_name}', provide the following JSON:
    {{
        "Calories": <integer>,  # Calories per serving
        "Protein": <float>,  # Protein per serving in grams
        "Carbs": <float>,  # Carbohydrates per serving in grams
        "Fats": <float>,  # Fats per serving in grams
        "Serving Size": <float>  # Serving size in grams
    }}
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant for estimating nutritional macros."},
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )

    raw_response = response.choices[0].message.content.strip()
    print("Agent 2 Raw Response:", raw_response)
    return extract_json(raw_response)


def agent_3(parsed_json, macros):
    """
    Resolves ambiguities, calculates total macros based on serving size,
    and stores the enriched data in the database.
    """
    import sqlite3
    from datetime import datetime

    quantity = float(parsed_json["Quantity"])  # Quantity in grams
    food_name = parsed_json["Item"]

    # Resolve dynamic dates
    corrected_timestamp = parsed_json["Time Eaten"]
    corrected_timestamp = resolve_dynamic_dates(corrected_timestamp)  # Handle "Today" and "Yesterday"
    corrected_timestamp = normalize_day_name(corrected_timestamp)  # Fix day names
    corrected_timestamp = normalize_month_name(corrected_timestamp)  # Fix month names

    # Parse the corrected timestamp
    timestamp = datetime.strptime(corrected_timestamp, "%I:%M %p, %A, %b %d, %Y")

    # Dynamic serving size and macros
    serving_size_grams = macros["Serving Size"]
    servings = quantity / serving_size_grams  # Calculate number of servings
    total_macros = {key: value * servings for key, value in macros.items() if key != "Serving Size"}

    # Enriched data for database insertion
    enriched_data = {
        "food_name": food_name,
        "quantity": quantity,
        "time_eaten": timestamp,
        **total_macros,
    }

    # Store enriched data in SQL database
    conn = sqlite3.connect("food_consumption.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO FoodConsumption (food_name, quantity, time_eaten, calories, protein, carbs, fats)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            enriched_data["food_name"],
            enriched_data["quantity"],
            enriched_data["time_eaten"],
            enriched_data["Calories"],
            enriched_data["Protein"],
            enriched_data["Carbs"],
            enriched_data["Fats"],
        ),
    )
    conn.commit()
    conn.close()

    return enriched_data


# Orchestrator: Process User Input
def process_user_input(user_input):
    """
    Orchestrates the 3-agent chain.
    """
    print("Agent 1: Parsing input...")
    parsed_json = agent_1(user_input)
    
    print("Agent 2: Estimating macros...")
    macros = agent_2(parsed_json)
    
    print("Agent 3: Enriching and storing data...")
    enriched_output = agent_3(parsed_json, macros)
    
    return enriched_output

# Main Function
if __name__ == "__main__":
    initialize_database()
    
    user_input = "I ate a handful of almonds this morning."
    result = process_user_input(user_input)
    
    print("Final Output:")
    print(result)
