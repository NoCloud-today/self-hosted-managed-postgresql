from typing import List, Optional, Dict, Any, Tuple
import psycopg2


class PostgresUtils:
    def __init__(self, db_params: Optional[Dict[str, Any]] = None):
        self.db_params = db_params or {
            "dbname": "postgres",
            "user": "postgres",
            "password": "postgres",
            "host": "pg",
            "port": "5432"
        }

    def _get_db_connection(self, dbname: Optional[str] = None) -> psycopg2.extensions.connection:
        params = self.db_params.copy()
        if dbname:
            params["dbname"] = dbname
        return psycopg2.connect(**params)

    def create_database(self, dbname: str) -> None:
        conn = self._get_db_connection()
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(f"CREATE DATABASE {dbname}")
        conn.close()

    def drop_database(self, dbname: str) -> None:
        conn = self._get_db_connection()
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(f"DROP DATABASE IF EXISTS {dbname}")
        conn.close()

    def create_table(self, dbname: str, table_name: str, columns: List[str]) -> None:
        with self._get_db_connection(dbname) as conn:
            with conn.cursor() as cur:
                columns_def = ", ".join(columns)
                cur.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_def})")
                conn.commit()

    def drop_table(self, dbname: str, table_name: str) -> None:
        with self._get_db_connection(dbname) as conn:
            with conn.cursor() as cur:
                cur.execute(f"DROP TABLE IF EXISTS {table_name}")
                conn.commit()

    def insert_data(self, dbname: str, table: str, values: List[str]) -> None:
        with self._get_db_connection(dbname) as conn:
            with conn.cursor() as cur:
                for value in values:
                    cur.execute(f"INSERT INTO {table} (data) VALUES ({value})")
                conn.commit()

    def execute_query(self, dbname: str, query:str) -> list[tuple[Any, ...]]:
        with self._get_db_connection(dbname) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                return cur.fetchall()

    def truncate_table(self, dbname: str, table: str) -> None:
        with self._get_db_connection(dbname) as conn:
            with conn.cursor() as cur:
                cur.execute(f"TRUNCATE TABLE {table}")
                conn.commit()
