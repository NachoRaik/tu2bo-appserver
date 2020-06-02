import os
import tempfile
import pytest

from app import create_app
from config import DevelopmentConfig

@pytest.fixture
def client():
    """A test client for the app."""
    app = create_app(DevelopmentConfig)
    return app.test_client()
