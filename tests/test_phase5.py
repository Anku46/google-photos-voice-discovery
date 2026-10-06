"""
tests/test_phase5.py — Phase 5 FastAPI tests.
"""

from fastapi.testclient import TestClient
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.app import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_auth_rejection():
    """Test that authenticated endpoints reject calls without API keys."""
    # Pipeline Run
    res1 = client.post("/api/pipeline/run")
    assert res1.status_code == 403
    
    # Copilot Chat
    res2 = client.post("/api/chat", json={"query": "test"})
    assert res2.status_code == 403

def test_auth_success(monkeypatch):
    """Test that authenticated endpoints accept calls with the correct API key."""
    # Mock the API secret
    monkeypatch.setenv("API_SECRET_KEY", "test-secret-123")
    
    # We expect a 500 or 409 or something since we aren't mocking the DB, 
    # but NOT a 403 Forbidden.
    headers = {"X-API-Key": "test-secret-123"}
    
    res1 = client.post("/api/pipeline/run", headers=headers)
    assert res1.status_code != 403
    
    res2 = client.post("/api/chat", json={"query": "test"}, headers=headers)
    assert res2.status_code != 403
