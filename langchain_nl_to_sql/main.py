from openai import OpenAI


client = OpenAI()
def generate_sql_query(prompt, schema_description):
    """
    Generate an SQL query based on the given English prompt and schema description.
    """
    system_message = f"""
    You are a helpful assistant that generates SQL queries.
    The database schema is as follows:
    - id: integer, primary key, auto-increment
    - food_name: text, the name of the food
    - quantity: integer, the quantity of the food eaten
    - time_eaten: datetime, the time when the food was eaten
    
    you will only provide sql queries and no other text, incase you are not explicitly able to generate a query just return Difficulty constructing query
    Always provide syntactically correct MySQL queries.
    """

    # Use the chat completion endpoint
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt},
        ],
        temperature=0,  # Keep deterministic outputs for SQL generation
    )
    
    # Extract the content of the assistant's reply
    return response.choices[0].message.content.strip()#response.choices[0].message['content'].strip()

# Example database schema description
schema_description = """
The database has a table named 'FoodConsumption' with the following columns:
- id: integer, primary key, auto-increment
- food_name: text, the name of the food
- quantity: integer, the quantity of the food eaten
- time_eaten: datetime, the time when the food was eaten
"""

# Example usage
english_query = "add 5 banana"
sql_query = generate_sql_query(english_query, schema_description)

print(sql_query)
