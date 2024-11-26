from typing import List, Dict, Any
from agents.agent_1 import agent_1
from agents.agent_2 import agent_2
from agents.agent_3 import agent_3_validate
from utils.db_utils import initialize_database, print_all_entries, store_in_database
from utils.pinecone_utils import initialize_pinecone, add_to_pinecone

def process_user_input(user_input: str) -> None:
    """
    Process user input through multiple agents to parse, validate, and store food consumption data.
    
    Args:
        user_input (str): Natural language input describing food consumption
        
    Flow:
        1. Parse natural language to structured JSON (agent_1)
        2. Extract macronutrient information (agent_2)
        3. Validate extracted data (agent_3)
        4. Store in vector database and SQL database
    """
    parsed_json_list = agent_1(user_input)
    pinecone_index = initialize_pinecone()

    for parsed_json in parsed_json_list:
        macros = agent_2(parsed_json)
        validated_macros = agent_3_validate(macros)
        
        # Store data in both databases
        add_to_pinecone(validated_macros, pinecone_index)
        store_in_database(validated_macros)

    print_all_entries()

def main():
    """Initialize application and database."""
    initialize_database()

if __name__ == "__main__":
    main()