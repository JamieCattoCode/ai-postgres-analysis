# Postgres Data Analysis
Analyse and update your postgres database using plain text.

Powered by Chat GPT 4.

## Usage
The idea of this repository is to retrieve or update data in your postgres database without having to use SQL statements.

Instead, you just enter your human language text and GPT 4 will complete your operation/retrieve your results.


### How to use yourself
1. Clone down the repository
2. Create a .env file with your OPEN_AI_API_KEY and DATABASE_URL (see .env.example)
3. Open the terminal and run `cd {path for this repo}`
4. Run `poetry install`
5. Run `poetry run start --prompt {your DB action in plain text}`
