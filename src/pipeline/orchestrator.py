"""
pipeline/orchestrator.py — Background pipeline orchestrator.
Manages sequential execution of pipeline stages and updates PIPELINE_RUNS in Supabase.
"""

import os
import sys
import traceback

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from db import upsert_pipeline_stage
from ingestion.play_store import scrape_play_store
from ingestion.app_store import scrape_app_store
from ingestion.reddit import scrape_reddit
from pipeline.filter import process_unfiltered_reviews
from pipeline.extract import process_extractions
from pipeline.classify import process_classifications
from pipeline.cluster import run_clustering
from pipeline.top_issues import compute_top_issues


def run_pipeline(run_id: str):
    """
    Executes the full pipeline sequentially. 
    Updates the PIPELINE_RUNS table for each stage.
    """
    stages = [
        ("ingest_play_store", scrape_play_store),
        ("ingest_app_store", scrape_app_store),
        ("ingest_reddit", scrape_reddit),
        ("filter", process_unfiltered_reviews),
        ("extract", process_extractions),
        ("classify", process_classifications),
        ("cluster", run_clustering),
        ("top_issues", compute_top_issues)
    ]
    
    # Initialize all to pending
    for name, _ in stages:
        upsert_pipeline_stage(run_id, name, "pending")
        
    for stage_name, stage_func in stages:
        upsert_pipeline_stage(run_id, stage_name, "running")
        try:
            print(f"--- Starting Pipeline Stage: {stage_name} ---")
            stage_func()
            upsert_pipeline_stage(run_id, stage_name, "done")
        except Exception as e:
            err_msg = str(e) + "\n" + traceback.format_exc()
            print(f"!!! Error in {stage_name} !!!\n{err_msg}")
            upsert_pipeline_stage(run_id, stage_name, "error", error_message=str(e))
            # Pause pipeline on first error
            break
            
    print(f"--- Pipeline run {run_id} finished ---")
