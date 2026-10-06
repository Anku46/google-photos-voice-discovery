"""
Pydantic v2 data contracts for the Google Photos Feedback Discovery Engine.
Phase 1.2 — all schemas used across the pipeline and API layer.

Design decisions (locked):
- instructor owns JSON mode; do NOT also set response_format manually.
- JourneyClassification carries primary_gap + optional secondary_gap.
- INSUFFICIENT_CONTEXT is a valid gap for reviews that lack enough detail.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from datetime import datetime


# ---------------------------------------------------------------------------
# Core enums
# ---------------------------------------------------------------------------

class RetrievalFailureGap(str, Enum):
    MEMORY_EXPRESSION = "Memory Expression Gap"
    INTERPRETATION = "Interpretation Gap"
    RETRIEVAL = "Retrieval Gap"
    RECOGNITION = "Recognition Gap"
    REFINEMENT = "Refinement Gap"
    INSUFFICIENT_CONTEXT = "Insufficient Context"  # [FIX] for ambiguous / detail-poor reviews


class FilterClassification(str, Enum):
    RETRIEVAL_EXPERIENCE = "RETRIEVAL_EXPERIENCE"
    GENERAL_APP_COMPLAINT = "GENERAL_APP_COMPLAINT"
    UNRELATED_FEATURE_REQUEST = "UNRELATED_FEATURE_REQUEST"
    GENERIC_SENTIMENT = "GENERIC_SENTIMENT"


# ---------------------------------------------------------------------------
# Pipeline schemas (LLM output contracts)
# ---------------------------------------------------------------------------

class MemoryClues(BaseModel):
    objects: List[str] = Field(default_factory=list, description="Physical objects remembered")
    people: List[str] = Field(default_factory=list, description="Identities, groups, or faces")
    places: List[str] = Field(default_factory=list, description="Locations, settings, or landmarks")
    events: List[str] = Field(default_factory=list, description="Occasions, gatherings, or activities")
    approximate_time: Optional[str] = Field(None, description="Fuzzy temporal references (e.g. 'last summer')")
    text_content: Optional[str] = Field(None, description="Words, document labels, or numbers visible in the photo")
    visual_cues: Optional[str] = Field(None, description="Colors, lighting, framing, composition")


class RetrievalExperienceExtraction(BaseModel):
    target_entity: str = Field(..., description="What the user was attempting to locate")
    memory_clues: MemoryClues
    search_attempt: Optional[str] = Field(None, description="Query or method used to search")
    outcome: str = Field(..., description="Observed system response")
    workaround: Optional[str] = Field(None, description="Manual or secondary action taken by the user")
    success: bool = Field(..., description="Whether the photo was eventually retrieved")


class JourneyClassification(BaseModel):
    """
    [FIX] primary_gap replaces the old single failure_gap field.
    secondary_gap is optional — assign it when a review clearly spans two gap types.
    """
    primary_gap: RetrievalFailureGap = Field(
        ..., description="The main breaking point in the user's retrieval journey"
    )
    secondary_gap: Optional[RetrievalFailureGap] = Field(
        None, description="Optional secondary gap when the review spans two failure types"
    )
    journey_stage_breakdown: str = Field(..., description="Step where the interaction failed")
    rationale: str = Field(..., description="Chain-of-thought justification")
    confidence: float = Field(..., ge=0.0, le=1.0)


class FilterResult(BaseModel):
    classification: FilterClassification
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str = Field(..., description="One-sentence reason for the classification")


class ClusterArchetype(BaseModel):
    theme_title: str = Field(..., description="Short, descriptive title for the problem cluster")
    primary_failure_gap: RetrievalFailureGap = Field(..., description="The dominant gap in this cluster")
    user_archetype: Optional[str] = Field(None, description="Representative user persona for this cluster")


class PMInsight(BaseModel):
    user_situation: str = Field(..., description="Context of what the user is trying to achieve")
    observed_behavior: str = Field(..., description="What the user did (search query, workaround)")
    retrieval_failure: str = Field(..., description="Why the system failed to return the expected result")
    likely_underlying_problem: str = Field(..., description="The root technical or UX issue")
    representative_quotes: List[str] = Field(
        ..., description="Exact quotes from the cluster — must be verbatim substrings of sanitized review text"
    )
    potential_opportunity: str = Field(..., description="Design or engineering opportunity to solve this class of problems")


# ---------------------------------------------------------------------------
# Ingestion / DB record schemas
# ---------------------------------------------------------------------------

class ReviewRecord(BaseModel):
    """A sanitized review record as stored in the REVIEWS table."""
    review_id: str
    source: str  # "play_store" | "app_store" | "reddit"
    review_text: str
    rating: Optional[int] = None
    review_date: Optional[datetime] = None
    app_version: Optional[str] = None
    language: str = "en"
    text_hash: str  # SHA-256 of normalized sanitized text


# ---------------------------------------------------------------------------
# API response models (one per endpoint — Phase 1.2)
# ---------------------------------------------------------------------------

class MetricsResponse(BaseModel):
    total_reviews: int
    relevant_reviews: int
    yield_percent: float
    gap_counts: dict  # {gap_name: count}
    cluster_count: int
    source_counts: dict  # {source: count}


class ClusterSummary(BaseModel):
    cluster_id: str
    cluster_title: str
    review_count: int
    dominant_gap: str
    medoid_quote: Optional[str] = None
    date_range: Optional[str] = None  # [FIX] recency: "2024-01 – 2025-03"
    recent_share: Optional[float] = None  # fraction from last 6 months


class ClusterListResponse(BaseModel):
    clusters: List[ClusterSummary]
    unclustered_count: int  # [FIX] HDBSCAN noise bucket exposed, not hidden


class DistributionEntry(BaseModel):
    gap: str
    primary_count: int
    secondary_count: int  # [FIX] secondary_gap overlay
    percentage: float


class DistributionResponse(BaseModel):
    """Renamed from /funnel — this is a distribution, not stage-to-stage drop-off."""
    entries: List[DistributionEntry]
    total_classified: int


class ReviewRow(BaseModel):
    review_id: str
    review_text: str
    source: str
    rating: Optional[int]
    review_date: Optional[datetime]
    primary_gap: Optional[str]
    secondary_gap: Optional[str]
    cluster_id: Optional[str]


class ReviewsResponse(BaseModel):
    reviews: List[ReviewRow]
    total: int
    page: int
    page_size: int


class TopIssueCard(BaseModel):
    rank: int
    title: str
    category: str
    review_count: int
    impact_score: float  # computed in code, not LLM-generated
    root_cause: str
    representative_quotes: List[str]
    recommendation: str


class TopIssuesResponse(BaseModel):
    issues: List[TopIssueCard]


class PipelineStatusResponse(BaseModel):
    run_id: Optional[str]
    current_stage: Optional[str]
    stages: dict  # {stage_name: "done" | "running" | "pending" | "error"}
    last_run_at: Optional[datetime]
    last_error: Optional[str]


class PipelineRunResponse(BaseModel):
    run_id: str
    message: str = "Pipeline started in background"


class ChatRequest(BaseModel):
    question: str
    conversation_id: Optional[str] = None


class CitedQuote(BaseModel):
    review_id: str
    text: str
    source: str


class ChatResponse(BaseModel):
    answer: str
    citations: List[CitedQuote]
    insufficient_data: bool = False  # True when the data cannot answer the question
