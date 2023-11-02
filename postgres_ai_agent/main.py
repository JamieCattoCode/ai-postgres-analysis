from postgres_ai_agent.modules.db import PostgresDB
from postgres_ai_agent.modules import llm
import os
import dotenv

dotenv.load_dotenv()

assert os.environ.get('DATABASE_URL'), "POSTGRES_CONNECTION_URL not found in .env file."
assert os.environ.get('OPEN_AI_API_KEY'), "OPEN_AI_API_KEY not found in .env file."

DB_URL = os.environ.get('DATABASE_URL')
OPEN_AI_API_KEY = os.environ.get('OPEN_AI_API_KEY')

def main():
    # parse prompt param using arg parse

    # connect to db with statement and create a db_manager
    with PostgresDB() as db:
        db.connect_with_url(DB_URL)

        users_table = db.get_all('users')

        print("Users table", users_table)
    
    # call db_manager.get_table_definitions_for_prompt() to get tables in prompt ready form

    # create two blank calls to llm.add_cap_ref() that update our current prompt passed in from cli

    # call llm.prompt to get a prompt_response variable

    # parse SQL response from prompt_response using SQL_QUERY_DELIMITER '---------'

    # call db_manager.run_sql() with the parsed sql

if __name__ == '__main__':
    main()