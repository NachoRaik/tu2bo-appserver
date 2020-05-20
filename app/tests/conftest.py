import os
import tempfile
import pytest

from config import TestingConfig
from mongoengine import connect, disconnect
from app import create_app

@pytest.fixture
def client():
    """A test client for the app."""
    app = create_app(TestingConfig)
    return app.test_client()