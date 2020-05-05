import os
import tempfile
import pytest

from app import app as fapp

@pytest.fixture
def client():
    """A test client for the app."""
    return fapp.test_client()
