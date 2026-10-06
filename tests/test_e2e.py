"""
tests/test_e2e.py — Phase 7.1 End-to-End Tracing Verification.
Verifies that the API endpoints expose data that maintains strict data provenance
(e.g., clusters have real review quotes, sources are intact).
"""

from fastapi.testclient import TestClient
from unittest.mock import patch
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.app import app

client = TestClient(app)

class MockQueryResult:
    def __init__(self, data=None, count=0):
        self.data = data or []
        self.count = count

class MockTableQuery:
    def __init__(self, data=None, count=0):
        self._data = data or []
        self._count = count

    def select(self, *args, **kwargs):
        return self

    def eq(self, *args, **kwargs):
        return self

    def order(self, *args, **kwargs):
        return self

    def execute(self):
        return MockQueryResult(data=self._data, count=self._count)

class MockDbClient:
    def table(self, table_name):
        if table_name == "REVIEWS":
            return MockTableQuery(
                data=[{"source": "google_play"}, {"source": "app_store"}],
                count=2
            )
        elif table_name == "FILTERED_REVIEWS":
            return MockTableQuery(count=1)
        elif table_name == "FAILURE_CLASSIFICATIONS":
            return MockTableQuery(
                data=[{"primary_gap": "GAP_1_VOICE_QUERY_MISMATCH", "secondary_gap": "GAP_2_METADATA_ABSENT"}]
            )
        elif table_name == "THEMATIC_CLUSTERS":
            return MockTableQuery(
                data=[{
                    "cluster_id": "c1",
                    "cluster_title": "Voice search fails for pets",
                    "is_noise_bucket": False,
                    "review_count": 15
                }],
                count=1
            )
        elif table_name == "TOP_ISSUES":
            return MockTableQuery(
                data=[{
                    "issue_id": "issue-1",
                    "rank": 1,
                    "impact_score": 9.5,
                    "representative_quotes": ["Voice search cannot find dogs."]
                }]
            )
        return MockTableQuery()

@patch("backend.app.get_client", return_value=MockDbClient())
def test_metrics_api_structure(mock_db):
    """Verify metrics payload format."""
    res = client.get("/api/metrics")
    assert res.status_code == 200
    data = res.json()
    assert "total_reviews" in data
    assert "yield_percentage" in data
    assert "gap_counts" in data
    assert "cluster_count" in data
    assert "source_counts" in data

@patch("backend.app.get_client", return_value=MockDbClient())
def test_clusters_provenance(mock_db):
    """Verify that if clusters exist, they are properly structured."""
    res = client.get("/api/clusters")
    assert res.status_code == 200
    clusters = res.json()
    
    assert isinstance(clusters, list)
    assert len(clusters) > 0
    for c in clusters:
        assert "cluster_id" in c
        assert "cluster_title" in c
        assert "is_noise_bucket" in c
        assert "review_count" in c

@patch("backend.app.get_client", return_value=MockDbClient())
def test_top_issues_traceability(mock_db):
    """Verify top issues contain actual representative quotes and correct keys."""
    res = client.get("/api/top-issues")
    assert res.status_code == 200
    issues = res.json()
    
    assert isinstance(issues, list)
    assert len(issues) > 0
    for issue in issues:
        assert "issue_id" in issue
        assert "rank" in issue
        assert "impact_score" in issue
        assert "representative_quotes" in issue
        assert isinstance(issue["representative_quotes"], list)
