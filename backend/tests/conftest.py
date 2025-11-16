import pytest
import os
from unittest.mock import patch

# Add the backend directory to the Python path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import init_db, get_db_path

@pytest.fixture(scope="session", autouse=True)
def test_db():
    """Fixture to set up and tear down a temporary database for the entire test session."""
    init_db()
    yield
    os.remove(get_db_path())
