import os
import tempfile
import pytest

from app import create_app
from config import TestingConfig

@pytest.fixture
def client():
    """A test client for the app."""
    app = create_app(TestingConfig)
    return app.test_client()
