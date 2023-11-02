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

    def run_sql(self, sql_statement):
        self.cur.execute(sql_statement)
        self.conn.commit()

    def get_table_definitions(self, table_name):
        get_def_sql = """
        SELECT pg_tables.tablename, pg_catalog.pg_get_tabledef(pg_tables.oid, true)
        FROM pg_tables
        WHERE tablename = %s;
        """
        self.cur.execute(get_def_sql, (table_name,))
        return self.cur.fetchone()[1]

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
