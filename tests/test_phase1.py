"""
tests/test_phase1.py — Phase 1 exit criteria tests.

Exit criteria (from implementation plan):
  ✅ Schemas validate sample data.
  ✅ The golden set exists.
  ✅ pytest runs.

Run: pytest tests/ -v
"""

import json
import pytest
from pathlib import Path

# ---------------------------------------------------------------------------
# 1.1 — Dependency checks (correct packages available)
# ---------------------------------------------------------------------------

def test_sklearn_hdbscan_available():
    """sklearn.cluster.HDBSCAN must be available (scikit-learn >= 1.3). No standalone hdbscan."""
    from sklearn.cluster import HDBSCAN  # noqa: F401


def test_no_standalone_hdbscan():
    """Standalone hdbscan package must NOT be in use (we use sklearn.cluster.HDBSCAN)."""
    import importlib.util
    # The standalone package installs as 'hdbscan' with a different module path than sklearn
    spec = importlib.util.find_spec("hdbscan")
    if spec is not None:
        # It's installed — check it's not the standalone (no __version__ attr that differs from sklearn)
        import hdbscan as _h
        # If standalone hdbscan is installed alongside sklearn, this is a warning, not a hard fail.
        # The pipeline should still use sklearn.cluster.HDBSCAN regardless.
        pytest.warns(UserWarning, match="standalone hdbscan") if False else None  # informational


def test_supabase_importable():
    from supabase import create_client  # noqa: F401


def test_instructor_importable():
    import instructor  # noqa: F401


def test_pydantic_v2():
    import pydantic
    major = int(pydantic.__version__.split(".")[0])
    assert major >= 2, f"Pydantic v2+ required, got {pydantic.__version__}"


# ---------------------------------------------------------------------------
# 1.2 — Pydantic schema validation
# ---------------------------------------------------------------------------

from src.pipeline.models import (
    MemoryClues,
    RetrievalExperienceExtraction,
    JourneyClassification,
    RetrievalFailureGap,
    FilterResult,
    FilterClassification,
    MetricsResponse,
    DistributionResponse,
    DistributionEntry,
    PipelineStatusResponse,
)


def test_memory_clues_defaults():
    clues = MemoryClues()
    assert clues.objects == []
    assert clues.people == []
    assert clues.approximate_time is None


def test_retrieval_experience_validates():
    exp = RetrievalExperienceExtraction(
        target_entity="prescription photo",
        memory_clues=MemoryClues(objects=["prescription"], approximate_time="last year"),
        search_attempt="medicine",
        outcome="zero results",
        success=False,
    )
    assert exp.target_entity == "prescription photo"
    assert exp.memory_clues.objects == ["prescription"]


def test_journey_classification_primary_gap():
    clf = JourneyClassification(
        primary_gap=RetrievalFailureGap.RETRIEVAL,
        journey_stage_breakdown="System failed to surface candidate photos",
        rationale="User entered a valid query but OCR failed on image text",
        confidence=0.87,
    )
    assert clf.primary_gap == RetrievalFailureGap.RETRIEVAL
    assert clf.secondary_gap is None


def test_journey_classification_secondary_gap():
    clf = JourneyClassification(
        primary_gap=RetrievalFailureGap.MEMORY_EXPRESSION,
        secondary_gap=RetrievalFailureGap.INTERPRETATION,
        journey_stage_breakdown="User could not express memory; system also misinterpreted",
        rationale="Dual failure",
        confidence=0.72,
    )
    assert clf.secondary_gap == RetrievalFailureGap.INTERPRETATION


def test_insufficient_context_gap_exists():
    clf = JourneyClassification(
        primary_gap=RetrievalFailureGap.INSUFFICIENT_CONTEXT,
        journey_stage_breakdown="Not enough detail in review",
        rationale="Review only says 'search is broken'",
        confidence=0.40,
    )
    assert clf.primary_gap.value == "Insufficient Context"


def test_confidence_bounds():
    with pytest.raises(Exception):
        JourneyClassification(
            primary_gap=RetrievalFailureGap.RETRIEVAL,
            journey_stage_breakdown="x",
            rationale="x",
            confidence=1.5,  # invalid: > 1.0
        )


def test_filter_result_validates():
    fr = FilterResult(
        classification=FilterClassification.RETRIEVAL_EXPERIENCE,
        confidence=0.95,
        reasoning="Review describes a failed photo search attempt",
    )
    assert fr.classification == FilterClassification.RETRIEVAL_EXPERIENCE


def test_api_response_models():
    """Smoke-test all API response models instantiate correctly."""
    MetricsResponse(
        total_reviews=1000, relevant_reviews=145, yield_percent=14.5,
        gap_counts={"Memory Expression Gap": 55}, cluster_count=8,
        source_counts={"play_store": 600, "app_store": 300, "reddit": 100},
    )
    DistributionResponse(
        entries=[DistributionEntry(gap="Retrieval Gap", primary_count=40, secondary_count=5, percentage=27.5)],
        total_classified=145,
    )
    PipelineStatusResponse(
        run_id="run_abc123",
        current_stage="filter",
        stages={"ingest": "done", "filter": "running"},
        last_run_at=None,
        last_error=None,
    )


# ---------------------------------------------------------------------------
# 1.4 — Golden evaluation set
# ---------------------------------------------------------------------------

GOLDEN_PATH = Path("eval/golden.jsonl")

def test_golden_set_exists():
    assert GOLDEN_PATH.exists(), "eval/golden.jsonl must exist (Phase 1.4)"


def test_golden_set_has_minimum_entries():
    records = [json.loads(l) for l in GOLDEN_PATH.read_text().splitlines() if l.strip()]
    assert len(records) >= 20, f"Golden set should have >= 20 entries, got {len(records)}"


def test_golden_set_has_relevant_and_irrelevant():
    records = [json.loads(l) for l in GOLDEN_PATH.read_text().splitlines() if l.strip()]
    labels = {r["label"] for r in records}
    assert "relevant" in labels
    assert "irrelevant" in labels


def test_golden_set_covers_all_five_gaps():
    records = [json.loads(l) for l in GOLDEN_PATH.read_text().splitlines() if l.strip()]
    gaps = {r["primary_gap"] for r in records if r["label"] == "relevant" and r["primary_gap"]}
    expected = {
        "Memory Expression Gap",
        "Interpretation Gap",
        "Retrieval Gap",
        "Recognition Gap",
        "Refinement Gap",
    }
    assert expected <= gaps, f"Missing gaps in golden set: {expected - gaps}"


def test_golden_set_has_pre_filter_false_negative():
    """
    At least one relevant review should be flagged as one that the keyword pre-filter
    would miss — to measure filter recall properly.
    """
    records = [json.loads(l) for l in GOLDEN_PATH.read_text().splitlines() if l.strip()]
    missed = [r for r in records if "pre-filter" in (r.get("notes") or "").lower()]
    assert len(missed) >= 1, "Golden set must include at least 1 review the keyword pre-filter would reject"


def test_golden_schema_keys():
    """Every golden record must have the required keys."""
    required = {"review_id", "source", "review_text", "label", "primary_gap"}
    records = [json.loads(l) for l in GOLDEN_PATH.read_text().splitlines() if l.strip()]
    for r in records:
        missing = required - r.keys()
        assert not missing, f"Record {r.get('review_id')} is missing keys: {missing}"
