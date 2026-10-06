"""
app.py — Phase 5 FastAPI Backend API.
"""

import os
import uuid
from typing import List, Optional
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, BackgroundTasks, Security, Depends
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

import sys
sys.path.append(os.path.dirname(__file__))

from db import get_client, get_latest_run_id, get_pipeline_status
from pipeline.orchestrator import run_pipeline
from pipeline.copilot import answer_copilot_query

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

app = FastAPI(title="Google Photos Discovery Engine API", version="2.0.0")

# CORS setup
origins_str = os.environ.get("ALLOWED_ORIGINS", "")
origins = [o.strip() for o in origins_str.split(",") if o.strip()]
if not origins:
    origins = ["http://localhost:5173", "http://localhost:3000"] # Fallbacks for local dev

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication
API_KEY_HEADER = APIKeyHeader(name="X-API-Key")

def verify_api_key(api_key: str = Security(API_KEY_HEADER)):
    expected = os.environ.get("API_SECRET_KEY")
    if not expected or api_key != expected:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

# --- Response Models ---
class CopilotRequest(BaseModel):
    query: str

class CopilotResponse(BaseModel):
    answer: str

class PipelineRunResponse(BaseModel):
    run_id: str
    message: str

class MetricsResponse(BaseModel):
    total_reviews: int
    yield_percentage: float
    gap_counts: dict
    cluster_count: int
    source_counts: dict

# --- Endpoints ---

@app.get("/health")
def health_check():
    """Railway health check."""
    return {"status": "ok"}

@app.get("/api/metrics", response_model=MetricsResponse)
def get_metrics():
    db = get_client()
    
    rev_count = db.table("REVIEWS").select("review_id", count="exact").execute().count or 0
    rel_count = db.table("FILTERED_REVIEWS").select("review_id", count="exact").eq("classification", "RETRIEVAL_EXPERIENCE").execute().count or 0
    
    yield_perc = (rel_count / rev_count * 100) if rev_count > 0 else 0.0
    
    # Gap counts
    cls_res = db.table("FAILURE_CLASSIFICATIONS").select("primary_gap").execute()
    gap_counts = {}
    for r in cls_res.data:
        g = r["primary_gap"]
        gap_counts[g] = gap_counts.get(g, 0) + 1
        
    # Cluster count (excluding noise)
    c_count = db.table("THEMATIC_CLUSTERS").select("cluster_id", count="exact").eq("is_noise_bucket", False).execute().count or 0
    
    # Source counts
    src_res = db.table("REVIEWS").select("source").execute()
    source_counts = {}
    for r in src_res.data:
        s = r["source"]
        source_counts[s] = source_counts.get(s, 0) + 1
        
    return MetricsResponse(
        total_reviews=rev_count,
        yield_percentage=yield_perc,
        gap_counts=gap_counts,
        cluster_count=c_count,
        source_counts=source_counts
    )

@app.get("/api/clusters")
def get_clusters():
    db = get_client()
    clusters = db.table("THEMATIC_CLUSTERS").select("*").execute()
    return clusters.data

@app.get("/api/clusters/{cluster_id}")
def get_cluster_detail(cluster_id: str):
    db = get_client()
    cluster = db.table("THEMATIC_CLUSTERS").select("*").eq("cluster_id", cluster_id).execute()
    if not cluster.data:
        raise HTTPException(status_code=404, detail="Cluster not found")
        
    insight = db.table("PM_INSIGHTS").select("*").eq("cluster_id", cluster_id).execute()
    
    # We would also fetch member reviews here if we stored the cluster assignment per review.
    # Since HDBSCAN is in-memory per run and we didn't map reviews->clusters in DB for Phase 4 simplicity,
    # we'll return the insight. To get members, we'd need a REVIEWS_CLUSTERS table.
    
    return {
        "cluster": cluster.data[0],
        "insight": insight.data[0] if insight.data else None
    }

@app.get("/api/distribution")
def get_distribution():
    db = get_client()
    cls_res = db.table("FAILURE_CLASSIFICATIONS").select("primary_gap, secondary_gap").execute()
    
    dist = {}
    for r in cls_res.data:
        pg = r["primary_gap"]
        sg = r.get("secondary_gap")
        if pg not in dist:
            dist[pg] = {"total": 0, "secondary": {}}
        dist[pg]["total"] += 1
        
        if sg:
            dist[pg]["secondary"][sg] = dist[pg]["secondary"].get(sg, 0) + 1
            
    return dist

@app.get("/api/top-issues")
def get_top_issues():
    db = get_client()
    res = db.table("TOP_ISSUES").select("*").order("rank").execute()
    return res.data

@app.post("/api/pipeline/run", response_model=PipelineRunResponse)
def trigger_pipeline(background_tasks: BackgroundTasks, api_key: str = Depends(verify_api_key)):
    """Non-blocking pipeline execution."""
    # Check if already running
    latest_id = get_latest_run_id()
    if latest_id:
        status = get_pipeline_status(latest_id)
        is_running = any(s["status"] in ("pending", "running") for s in status)
        if is_running:
            raise HTTPException(status_code=409, detail="A pipeline run is already in progress.")
            
    run_id = f"run_{uuid.uuid4().hex[:8]}"
    background_tasks.add_task(run_pipeline, run_id)
    return PipelineRunResponse(run_id=run_id, message="Pipeline execution started in the background.")

@app.get("/api/pipeline/status")
def get_status():
    latest_id = get_latest_run_id()
    if not latest_id:
        return {"status": "No runs found"}
        
    status = get_pipeline_status(latest_id)
    return {
        "run_id": latest_id,
        "stages": status
    }

@app.post("/api/chat", response_model=CopilotResponse)
def copilot_chat(req: CopilotRequest, api_key: str = Depends(verify_api_key)):
    """RAG Copilot endpoint."""
    try:
        answer = answer_copilot_query(req.query)
        return CopilotResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
