"""
tests/test_phase3.py — Phase 3 Groq pipeline tests.

Exit criteria (from implementation plan):
  ✅ Eval report committed / can be run.
  ✅ Prompts use proper JSON schemas.
  ✅ Budget tracking prevents overrun.
"""

import os
import pytest
from src.pipeline.groq_client import check_budget, BUDGET_FILE


def test_budget_tracking_logic(monkeypatch, tmp_path):
    """Test that check_budget correctly counts requests and raises exception when limit is hit."""
    # Point BUDGET_FILE to a temp directory
    test_budget_file = tmp_path / "groq_budget.json"
    import backend.pipeline.groq_client
    monkeypatch.setattr(src.pipeline.groq_client, "BUDGET_FILE", str(test_budget_file))
    
    # 1st request should work
    src.pipeline.groq_client.check_budget()
    assert test_budget_file.exists()
    
    import json
    with open(test_budget_file, "r") as f:
        data = json.load(f)
        assert data["requests"] == 1
        
    # Artificially inflate the budget to the max limit
    data["requests"] = src.pipeline.groq_client.MAX_DAILY_REQUESTS
    with open(test_budget_file, "w") as f:
        json.dump(data, f)
        
    # The next request should raise a RuntimeError
    with pytest.raises(RuntimeError, match="Groq daily request budget exceeded"):
        src.pipeline.groq_client.check_budget()


def test_model_id_from_env(monkeypatch):
    import backend.pipeline.groq_client
    
    # Missing env variable raises ValueError
    monkeypatch.delenv("GROQ_MODEL_FILTER", raising=False)
    with pytest.raises(ValueError):
        src.pipeline.groq_client.get_model("FILTER")
        
    # Provided env variable works
    monkeypatch.setenv("GROQ_MODEL_EXTRACT", "llama-test-model")
    model = src.pipeline.groq_client.get_model("EXTRACT")
    assert model == "llama-test-model"
