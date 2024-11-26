import re
import json

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