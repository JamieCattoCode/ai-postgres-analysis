import psycopg2
from psycopg2 import sql

class PostgresDB:
    def __init__(self):
        self.conn = None
        self.cur = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()

    def connect_with_url(self, url):
        self.conn = psycopg2.connect(url)
        self.cur = self.conn.cursor()

    def upsert(self, table_name, _dict):
        columns = _dict.keys()
        values = [sql.Identifier(col) for col in columns]
        upsert_sql = sql.SQL(
            "INSERT INTO {} ({}) VALUES ({}) ON CONFLICT (id) DO UPDATE SET {}"
        ).format(
            sql.Identifier(table_name),
            sql.SQL(', ').join(values),
            sql.SQL(', ').join([sql.Placeholder() for _ in values]),
            sql.SQL(', ').join([sql.Identifier(col) + sql.SQL(" = EXCLUDED.") + sql.Identifier(col) for col in columns])
        )
        self.cur.execute(upsert_sql, list(_dict.values()))
        self.conn.commit()

    def delete(self, table_name, _id):
        delete_sql = sql.SQL("DELETE FROM {} WHERE id = %s").format(sql.Identifier(table_name))
        self.cur.execute(delete_sql, (_id,))
        self.conn.commit()

    def get(self, table_name, _id):
        select_sql = sql.SQL("SELECT * FROM {} WHERE id = %s").format(sql.Identifier(table_name))
        self.cur.execute(select_sql, (_id,))
        return self.cur.fetchone()

    def get_all(self, table_name):
        select_sql = sql.SQL("SELECT * FROM {}").format(sql.Identifier(table_name))
        self.cur.execute(select_sql)
        return self.cur.fetchall()

    def run_sql(self, sql):
        self.cur.execute(sql)
        # Determine if the SQL statement is a SELECT statement
        if self.cur.description:
            # If it is a SELECT statement, fetch the results
            return self.cur.fetchall()
        else:
            # If it's not a SELECT statement, it's an action, commit it if autocommit is disabled
            self.conn.commit()
            return self.cur.rowcount 

    def get_table_definitions(self, table_name):
        # Query to retrieve the column definitions
        column_def_sql = """
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = %s
            ORDER BY ordinal_position;
        """

        self.cur.execute(column_def_sql, (table_name,))
        columns = self.cur.fetchall()

        # Start the CREATE TABLE command
        create_table_sql = f"CREATE TABLE {table_name} (\n"

        # List of column definitions
        column_definitions = []

        for column in columns:
            column_name, data_type, is_nullable, column_default = column
            column_def = f"    {column_name} {data_type}"
            if column_default is not None:
                column_def += f" DEFAULT {column_default}"
            if is_nullable == "NO":
                column_def += " NOT NULL"
            column_definitions.append(column_def)

        # Combine column definitions and close the CREATE TABLE command
        create_table_sql += ",\n".join(column_definitions)
        create_table_sql += "\n);"

        return create_table_sql


    def get_all_table_names(self):
        select_sql = "SELECT tablename FROM pg_tables WHERE schemaname='public';"
        self.cur.execute(select_sql)
        return [row[0] for row in self.cur.fetchall()]

    def get_table_definitions_for_prompt(self):
        table_names = self.get_all_table_names()
        definitions = []
        for table in table_names:
            definitions.append(self.get_table_definitions(table))
        return '\n'.join(definitions)

# Example usage
