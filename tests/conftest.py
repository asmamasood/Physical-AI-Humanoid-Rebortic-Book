import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

@pytest.fixture
def client():
    """Create a TestClient for the FastAPI app."""
    return TestClient(app)

@pytest.fixture
def mock_settings(monkeypatch):
    """Mock environment variables for testing."""
    monkeypatch.setenv("COHERE_API_KEY", "mock_key")
    monkeypatch.setenv("QDRANT_URL", "http://mock-qdrant")
    monkeypatch.setenv("QDRANT_API_KEY", "mock_key")
    monkeypatch.setenv("GEMINI_API_KEY", "mock_key")
    monkeypatch.setenv("ADMIN_SECRET", "mock_secret")
