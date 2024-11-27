import json
from openai import OpenAI
from ..utils.json_utils import extract_json
from typing import Dict, Any

client = OpenAI()

def agent_3_validates(macros: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates the calculated macros by double-checking against known nutritional data.
    Returns validated macros or raises an exception if validation fails.
    """
    print("------------------> Agent 3 Request: validating macros for", macros["Item"], macros["Quantity"])
    prompt = f"""
    You are a nutrition validation expert. Verify if the following macros are reasonable for the given item and quantity.
    If they are reasonable, return the same JSON. If they need adjustment, provide corrected values.
    Return the COMPLETE JSON object including all original fields.
    
    {json.dumps(macros, indent=2)}

    Respond with a JSON object only, using the exact same structure as the input.
    If the macro values are significantly off, adjust them to realistic values.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a nutrition validation expert."},
            {"role": "user", "content": prompt},
        ],
        temperature=0
    )
    
    validated_macros = extract_json(response.choices[0].message.content.strip())
    print("------------------> Agent 3 Response: Validated macros", validated_macros)
    return validated_macros
