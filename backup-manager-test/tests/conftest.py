from typing import Generator

import pytest

from tests.utils.db_utils import PostgresUtils
from tests.utils.backup_client import BackupClient


@pytest.fixture(scope="session")
def backup_client() -> BackupClient:
    return BackupClient()


@pytest.fixture(scope="session")
def db_utils():
    return PostgresUtils()


@pytest.fixture(scope="session")
def test_database(db_utils: PostgresUtils) -> Generator[str, None, None]:
    db_name = "testdb"
    db_utils.drop_database(db_name)
    db_utils.create_database(db_name)

    yield db_name

    db_utils.drop_database(db_name)


@pytest.fixture(scope="function")
def test_table(db_utils: PostgresUtils, test_database: str) -> Generator[str, None, None]:
    table_name = "test_table"
    columns = [
        "id serial PRIMARY KEY",
        "data text",
        "created_at timestamp DEFAULT CURRENT_TIMESTAMP"
    ]

    db_utils.create_table(test_database, table_name, columns)

    yield table_name

    db_utils.drop_table(test_database, table_name)


@pytest.fixture(scope="function")
def test_data(db_utils: PostgresUtils, test_database: str, test_table: str) -> Generator[None, None, None]:
    values = ["'test_data_1'", "'test_data_2'", "'test_data_3'"]
    db_utils.insert_data(test_database, test_table, values)
    yield
    db_utils.truncate_table(test_database, test_table)
