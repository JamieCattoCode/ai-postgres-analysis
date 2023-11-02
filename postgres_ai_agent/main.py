from postgres_ai_agent.modules.db import PostgresDB
from postgres_ai_agent.modules import llm
import os
import dotenv
from autogen import (
    AssistantAgent,
    UserProxyAgent,
    GroupChat,
    GroupChatManager,
    config_list_from_json,
    config_list_from_models,
)

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

        # build the gpt_configuration object

        # build the function map

        # create our terminate msg function

        # create a set of agents
        admin = UserProxyAgent(
            name="Admin",
            system_message="Admin. Takes in the prompt and manages the group chat.",
            code_execution_config=False,
        )
        engineer = AssistantAgent(
            name="Data Engineer",
            llm_config=gpt4_config,
            system_message="Data Engineer. Generates the SQL query.",
        )
        analyst = AssistantAgent(
            name="Senior Data Analyst",
            llm_config=gpt4_config,
            system_message="Senior Data Analyst. Runs the SQL query and generates the response.",
        )
        manager = AssistantAgent(
            name="Product Manager",
            llm_config=gpt4_config,
            system_message="Product Manager. Validates the response to make sure it's correct.",
        )

        # create a group chat and initiate the chat


if __name__ == '__main__':
    main()
