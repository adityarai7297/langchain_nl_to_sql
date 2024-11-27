import re
import json
from datetime import datetime
from openai import OpenAI
from typing import List, Dict, Any


client = OpenAI()

def agent_1_identifies(user_input: str) -> List[Dict[str, Any]]:
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
    
    # Parse and return the JSON list
    return json.loads(cleaned_response)