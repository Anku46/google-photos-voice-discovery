"""
tests/test_phase5.py — Phase 5 FastAPI tests.
"""

from fastapi.testclient import TestClient
from unittest.mock import patch
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.app import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_auth_rejection():
    """Test that authenticated endpoints reject calls without API keys."""
    # Pipeline Run
    res1 = client.post("/api/pipeline/run")
    assert res1.status_code in [401, 403]
    
    # Copilot Chat
    res2 = client.post("/api/chat", json={"query": "test"})
    assert res2.status_code in [401, 403]

@patch("backend.app.get_latest_run_id", return_value=None)
@patch("backend.app.run_pipeline")
@patch("backend.app.answer_copilot_query", return_value="Mock response")
def test_auth_success(mock_chat, mock_run, mock_latest, monkeypatch):
    """Test that authenticated endpoints accept calls with the correct API key."""
    monkeypatch.setenv("API_SECRET_KEY", "test-secret-123")
    headers = {"X-API-Key": "test-secret-123"}
    
    res1 = client.post("/api/pipeline/run", headers=headers)
    assert res1.status_code == 200
    
    res2 = client.post("/api/chat", json={"query": "test"}, headers=headers)
    assert res2.status_code == 200
    assert res2.json() == {"answer": "Mock response"}
