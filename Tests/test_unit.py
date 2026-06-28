import pytest
import os
from storage.database import init_db

@pytest.fixture
def test_conn():
    """Create a fresh test database, yield it for the test, then delete it."""
    conn = init_db("database/test.db")
    yield conn                          # test runs here
    conn.close()
    os.remove("database/test.db")      # deleted after test finishes