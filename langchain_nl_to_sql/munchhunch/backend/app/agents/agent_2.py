from openai import OpenAI
from ..utils.json_utils import extract_json
from typing import Dict, Any

client = OpenAI()

def agent_2_calculates(parsed_json: Dict[str, Any]) -> Dict[str, Any]:
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
