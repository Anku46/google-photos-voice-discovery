"""
db.py — Supabase database layer for the Google Photos Feedback Discovery Engine.

Phase 1.3 (v2):
- Connects to Supabase via the official Python client.
- Creates all required tables via SQL if they don't exist (run once, or via Supabase migrations).
- Tables: REVIEWS, FILTERED_REVIEWS, RETRIEVAL_EXPERIENCES, FAILURE_CLASSIFICATIONS,
          THEMATIC_CLUSTERS, PM_INSIGHTS, PIPELINE_RUNS, TOP_ISSUES.
- Row-level security (RLS) must be enabled separately in the Supabase dashboard (Step 1.5).

Environment variables required (never hardcode):
    SUPABASE_URL          — your project URL (https://xxx.supabase.co)
    SUPABASE_SERVICE_KEY  — service role key (server-only, never sent to browser)
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

_client: Client | None = None


def get_client() -> Client:
    """Return a cached Supabase client. Raises if env vars are not set."""
    global _client
    if _client is None:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_KEY")
        if not url or not key:
            raise RuntimeError(
                "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in environment variables."
            )
        _client = create_client(url, key)
    return _client


# ---------------------------------------------------------------------------
# Table creation SQL
# Run this once against your Supabase project (via psql, Supabase SQL editor,
# or a migration script). The schema reflects Phase 1.3 requirements.
# ---------------------------------------------------------------------------

SCHEMA_SQL = """
-- REVIEWS: sanitized-only store. Raw PII never reaches this table.
CREATE TABLE IF NOT EXISTS REVIEWS (
    review_id       TEXT PRIMARY KEY,
    source          TEXT NOT NULL,          -- 'play_store' | 'app_store' | 'reddit'
    review_text     TEXT NOT NULL,          -- sanitized text
    rating          INTEGER,
    review_date     TIMESTAMPTZ,
    app_version     TEXT,
    language        TEXT NOT NULL DEFAULT 'en',
    text_hash       TEXT UNIQUE NOT NULL,   -- SHA-256 of normalized sanitized text
    ingested_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- FILTERED_REVIEWS: LLM relevance classifier output (Stage 3)
CREATE TABLE IF NOT EXISTS FILTERED_REVIEWS (
    filter_id           TEXT PRIMARY KEY,
    review_id           TEXT NOT NULL REFERENCES REVIEWS(review_id),
    classification      TEXT NOT NULL,      -- FilterClassification enum value
    confidence_score    REAL,
    reasoning           TEXT,
    reject_reason       TEXT,               -- logged for every rejected review [FIX]
    evaluated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- RETRIEVAL_EXPERIENCES: structured extraction output (Stage 4)
CREATE TABLE IF NOT EXISTS RETRIEVAL_EXPERIENCES (
    experience_id       TEXT PRIMARY KEY,
    review_id           TEXT NOT NULL REFERENCES REVIEWS(review_id),
    target_entity       TEXT,
    memory_clues        JSONB,
    search_attempt      TEXT,
    outcome_description TEXT,
    workaround_used     TEXT,
    retrieval_success   BOOLEAN
);

-- FAILURE_CLASSIFICATIONS: gap classification output (Stage 5)
CREATE TABLE IF NOT EXISTS FAILURE_CLASSIFICATIONS (
    classification_id       TEXT PRIMARY KEY,
    experience_id           TEXT NOT NULL REFERENCES RETRIEVAL_EXPERIENCES(experience_id),
    primary_gap             TEXT NOT NULL,  -- [FIX] primary_gap (was failure_gap)
    secondary_gap           TEXT,           -- [FIX] optional secondary gap
    journey_stage_breakdown TEXT,
    rationale               TEXT,
    confidence              REAL
);

-- THEMATIC_CLUSTERS: HDBSCAN cluster metadata (Stage 6)
CREATE TABLE IF NOT EXISTS THEMATIC_CLUSTERS (
    cluster_id          TEXT PRIMARY KEY,
    cluster_title       TEXT,
    cluster_description TEXT,
    review_count        INTEGER,
    prevalence_rate     REAL,
    primary_failure_gap TEXT,
    date_range_start    DATE,               -- [FIX] recency tracking
    date_range_end      DATE,
    recent_share        REAL,               -- fraction from last 6 months
    is_noise_bucket     BOOLEAN DEFAULT FALSE  -- [FIX] TRUE for the HDBSCAN label=-1 bucket
);

-- PM_INSIGHTS: synthesized insights per cluster (Stage 7)
CREATE TABLE IF NOT EXISTS PM_INSIGHTS (
    insight_id                  TEXT PRIMARY KEY,
    cluster_id                  TEXT NOT NULL REFERENCES THEMATIC_CLUSTERS(cluster_id),
    user_situation              TEXT,
    observed_behavior           TEXT,
    retrieval_failure           TEXT,
    likely_underlying_problem   TEXT,
    representative_quotes       JSONB,      -- verified substrings of sanitized text only
    potential_opportunity       TEXT,
    synthesized_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- PIPELINE_RUNS: per-stage status log for the resumable orchestrator [FIX]
CREATE TABLE IF NOT EXISTS PIPELINE_RUNS (
    run_id          TEXT NOT NULL,
    stage           TEXT NOT NULL,          -- e.g. 'ingest', 'sanitize', 'filter', ...
    status          TEXT NOT NULL,          -- 'pending' | 'running' | 'done' | 'error'
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    error_message   TEXT,
    PRIMARY KEY (run_id, stage)
);

-- TOP_ISSUES: Stage 8 output, rankings computed in code (not LLM-generated) [FIX]
CREATE TABLE IF NOT EXISTS TOP_ISSUES (
    issue_id                TEXT PRIMARY KEY,
    rank                    INTEGER NOT NULL,
    title                   TEXT NOT NULL,
    category                TEXT,
    review_count            INTEGER NOT NULL,
    impact_score            REAL NOT NULL,
    root_cause              TEXT,
    representative_quotes   JSONB,
    recommendation          TEXT,
    generated_at            TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""


def print_schema():
    """Print the schema SQL — paste into Supabase SQL editor or a migration file."""
    print(SCHEMA_SQL)


# ---------------------------------------------------------------------------
# Helper: check Supabase connection
# ---------------------------------------------------------------------------

def ping() -> bool:
    """Return True if Supabase is reachable. Used by GET /health."""
    try:
        db = get_client()
        # A lightweight query — just fetch one row from any table.
        db.table("REVIEWS").select("review_id").limit(1).execute()
        return True
    except Exception as e:
        print(f"[db.ping] Supabase connection failed: {e}")
        return False


# ---------------------------------------------------------------------------
# Review helpers
# ---------------------------------------------------------------------------

def insert_review(record: dict) -> bool:
    """
    Insert a single sanitized review. Returns True on success, False if duplicate.
    The text_hash UNIQUE constraint naturally enforces deduplication.
    """
    db = get_client()
    try:
        db.table("REVIEWS").insert(record).execute()
        return True
    except Exception as e:
        if "duplicate" in str(e).lower() or "unique" in str(e).lower():
            return False  # deduplicated
        raise


def get_existing_hashes() -> set[str]:
    """Return all text_hash values currently in REVIEWS for incremental ingestion."""
    db = get_client()
    response = db.table("REVIEWS").select("text_hash").execute()
    return {row["text_hash"] for row in response.data}


# ---------------------------------------------------------------------------
# Pipeline run helpers
# ---------------------------------------------------------------------------

def upsert_pipeline_stage(run_id: str, stage: str, status: str,
                           error_message: str | None = None) -> None:
    """Update or insert a pipeline stage row in PIPELINE_RUNS."""
    from datetime import datetime, timezone
    db = get_client()
    now = datetime.now(timezone.utc).isoformat()
    row = {
        "run_id": run_id,
        "stage": stage,
        "status": status,
        "error_message": error_message,
    }
    if status == "running":
        row["started_at"] = now
    elif status in ("done", "error"):
        row["completed_at"] = now
    db.table("PIPELINE_RUNS").upsert(row).execute()


def get_pipeline_status(run_id: str) -> list[dict]:
    """Return all stage rows for a given run_id."""
    db = get_client()
    response = (
        db.table("PIPELINE_RUNS")
        .select("*")
        .eq("run_id", run_id)
        .order("started_at")
        .execute()
    )
    return response.data


def get_latest_run_id() -> str | None:
    """Return the most recent run_id, or None if no runs exist."""
    db = get_client()
    response = (
        db.table("PIPELINE_RUNS")
        .select("run_id, started_at")
        .order("started_at", desc=True)
        .limit(1)
        .execute()
    )
    if response.data:
        return response.data[0]["run_id"]
    return None


if __name__ == "__main__":
    # Utility: print the schema SQL for pasting into Supabase SQL editor.
    print("=== Schema SQL (paste into Supabase SQL editor) ===")
    print_schema()
    print("\n=== Pinging Supabase ===")
    print("Connected:", ping())
