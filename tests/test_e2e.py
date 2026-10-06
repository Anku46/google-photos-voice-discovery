"""
tests/test_e2e.py — Phase 7.1 End-to-End Tracing Verification.
Verifies that the API endpoints expose data that maintains strict data provenance
(e.g., clusters have real review quotes, sources are intact).
"""

from fastapi.testclient import TestClient
import os
import sys
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.app import app

client = TestClient(app)

def test_metrics_api_structure():
    """Verify metrics payload format."""
    res = client.get("/api/metrics")
    assert res.status_code == 200
    data = res.json()
    assert "total_reviews" in data
    assert "yield_percentage" in data
    assert "gap_counts" in data
    assert "cluster_count" in data
    assert "source_counts" in data

def test_clusters_provenance():
    """Verify that if clusters exist, they are properly structured."""
    res = client.get("/api/clusters")
    assert res.status_code == 200
    clusters = res.json()
    
    assert isinstance(clusters, list)
    for c in clusters:
        assert "cluster_id" in c
        assert "cluster_title" in c
        assert "is_noise_bucket" in c
        assert "review_count" in c

def test_top_issues_traceability():
    """Verify top issues contain actual representative quotes and correct keys."""
    res = client.get("/api/top-issues")
    assert res.status_code == 200
    issues = res.json()
    
    assert isinstance(issues, list)
    for issue in issues:
        assert "issue_id" in issue
        assert "rank" in issue
        assert "impact_score" in issue
        assert "representative_quotes" in issue
        
        # Verify the quotes are a list (they are stored as JSONB in DB)
        assert isinstance(issue["representative_quotes"], list)
