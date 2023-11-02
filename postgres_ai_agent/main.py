from postgres_ai_agent.modules.db import PostgresDB
from postgres_ai_agent.modules import llm
import os
import dotenv

dotenv.load_dotenv()

assert os.environ.get('DATABASE_URL'), "POSTGRES_CONNECTION_URL not found in .env file."
assert os.environ.get('OPEN_AI_API_KEY'), "OPEN_AI_API_KEY not found in .env file."

DB_URL = os.environ.get('DATABASE_URL')
OPEN_AI_API_KEY = os.environ.get('OPEN_AI_API_KEY')

import argparse

def main():
    # parse prompt param using arg parse
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt", help="Prompt for the AI")
    args = parser.parse_args()

    # connect to db with statement and create a db_manager
    with PostgresDB() as db:
        db.connect_with_url(DB_URL)

        # call db_manager.get_table_definitions_for_prompt() to get tables in prompt ready form
        table_definitions = db.get_table_definitions_for_prompt()

        # create two blank calls to llm.add_cap_ref() that update our current prompt passed in from cli
        prompt = llm.add_cap_ref(args.prompt, "", "TABLE_DEFINITIONS", table_definitions)
        prompt = llm.add_cap_ref(prompt, "", "DATABASE_URL", DB_URL)

        # call llm.prompt to get a prompt_response variable
        prompt_response = llm.prompt(prompt)

        # parse SQL response from prompt_response using SQL_QUERY_DELIMITER '---------'
        sql_statements = prompt_response.split('---------')

        # call db_manager.run_sql() with the parsed sql
        for sql in sql_statements:
            db.run_sql(sql)

if __name__ == '__main__':
    main()
