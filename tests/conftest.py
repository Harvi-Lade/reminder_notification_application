import pytest
from database.db_manager import DBManager


@pytest.fixture
def db_manager():
    manager = DBManager(db_name=":memory:", create_table=True)
    yield manager
    # Clean up after each test by dropping the table
    manager.execute("DROP TABLE IF EXISTS reminders")
