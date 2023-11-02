from postgres_ai_agent.modules.db import PostgresDB
from postgres_ai_agent.modules import llm
import os
import dotenv

dotenv.load_dotenv()

assert os.environ.get('DATABASE_URL'), "POSTGRES_CONNECTION_URL not found in .env file."
assert os.environ.get('OPEN_AI_API_KEY'), "OPEN_AI_API_KEY not found in .env file."

DB_URL = os.environ.get('DATABASE_URL')
OPEN_AI_API_KEY = os.environ.get('OPEN_AI_API_KEY')

POSTGRES_TABLE_DEFINITIONS_CAP_REF = "TABLE_DEFINITIONS"
TABLE_RESPONSE_FORMAT_CAP_REF = "TABLE_RESPONSE_FORMAT"
EXAMPLE_SELECT_CAP_REF = "EXAMPLE_SELECT"

SQL_DELIMITER = "----------"

import argparse

def main():
    # parse prompt param using arg parse
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", help="Prompt for the AI")
    args = parser.parse_args()

    if not args.prompt:
        print('Please provide a prompt.')
        return

    # connect to db with statement and create a db_manager
    with PostgresDB() as db:
        db.connect_with_url(DB_URL)
        print('Prompt v1: ', args.prompt)

        # call db_manager.get_table_definitions_for_prompt() to get tables in prompt ready form
        table_definitions = db.get_table_definitions_for_prompt()

        # create two blank calls to llm.add_cap_ref() that update our current prompt passed in from cli
        prompt = llm.add_cap_ref(
            args.prompt, 
            f"Use these {POSTGRES_TABLE_DEFINITIONS_CAP_REF} to satisfy the database query.", 
            POSTGRES_TABLE_DEFINITIONS_CAP_REF, 
            table_definitions
        )

        print('Prompt v2: ', prompt)

        prompt = llm.add_cap_ref(
            prompt, 
            f"\nYou must respond in the format {TABLE_RESPONSE_FORMAT_CAP_REF}. You must simply put your answers instead of the <>. Do not write anything extra. Do not add headings, colons, or apply your own formatting.", 
            TABLE_RESPONSE_FORMAT_CAP_REF, 
            f"""<explanation of the SQL query goes here>
{SQL_DELIMITER}
<SQL query exclusively as raw text goes here>
            """
        )

        # call llm.prompt to get a prompt_response variable
        prompt_response = llm.prompt(prompt)

        print('Prompt response: ', prompt_response)

        # parse SQL response from prompt_response using SQL_QUERY_DELIMITER '---------'


        # call db_manager.run_sql() with the parsed sql
        try:
            sql_statement = prompt_response.split(SQL_DELIMITER)[1].strip()
            result = db.run_sql(sql_statement)
        except:
            prompt_response = llm.prompt(prompt)
            print('Regenerated prompt response: ', prompt_response)

            sql_statement = prompt_response.split(SQL_DELIMITER)[1].strip()
            result = db.run_sql(sql_statement)

        print('Result: ', result)

if __name__ == '__main__':
    main()
