"""
pipeline/top_issues.py — Stage 8: Top Issues Synthesis (Phase 5).
Reads thematic clusters and PM insights, computes an impact score, and writes to TOP_ISSUES.
"""

import os
import sys
import uuid
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from db import get_client


def compute_top_issues(limit: int = 5):
    """
    Computes top issues by ranking clusters based on size and recency.
    Writes the results into the TOP_ISSUES table, replacing old rankings.
    """
    db = get_client()
    
    # Fetch clusters (excluding noise bucket)
    clusters_res = db.table("THEMATIC_CLUSTERS").select("*").eq("is_noise_bucket", False).execute()
    clusters = clusters_res.data
    
    if not clusters:
        print("No thematic clusters found to generate top issues.")
        return
        
    # Fetch PM insights
    insights_res = db.table("PM_INSIGHTS").select("*").execute()
    insights_map = {row["cluster_id"]: row for row in insights_res.data}
    
    # Calculate impact score
    # Impact = review_count * (1.0 + recent_share)
    # This boosts issues that are currently happening.
    for c in clusters:
        count = c.get("review_count", 0)
        recent = c.get("recent_share", 0.0) or 0.0
        c["_impact_score"] = count * (1.0 + recent)
        
    # Sort by impact score desc
    clusters.sort(key=lambda x: x["_impact_score"], reverse=True)
    top_clusters = clusters[:limit]
    
    # Clear existing TOP_ISSUES
    # Supabase Python client delete() requires a filter. We can just delete all by not using eq, but actually it might require a filter.
    # We will just fetch existing IDs and delete them.
    existing = db.table("TOP_ISSUES").select("issue_id").execute()
    for row in existing.data:
        db.table("TOP_ISSUES").delete().eq("issue_id", row["issue_id"]).execute()
        
    print(f"Generating top {limit} issues based on impact score...")
    
    for rank, c in enumerate(top_clusters, start=1):
        insight = insights_map.get(c["cluster_id"], {})
        
        issue_id = f"iss_{uuid.uuid4().hex[:8]}"
        
        # Read quotes properly
        quotes_raw = insight.get("representative_quotes", "[]")
        if isinstance(quotes_raw, str):
            try:
                quotes = json.loads(quotes_raw)
            except:
                quotes = []
        else:
            quotes = quotes_raw
            
        db.table("TOP_ISSUES").insert({
            "issue_id": issue_id,
            "rank": rank,
            "title": c.get("cluster_title", "Unknown Issue"),
            "category": c.get("primary_failure_gap", "Unknown"),
            "review_count": c.get("review_count", 0),
            "impact_score": c["_impact_score"],
            "root_cause": insight.get("likely_underlying_problem", ""),
            "representative_quotes": json.dumps(quotes),
            "recommendation": insight.get("potential_opportunity", "")
        }).execute()
        
        print(f"#{rank}: {c.get('cluster_title')} (Impact: {c['_impact_score']:.2f})")
        
    print("Top issues generated successfully.")

if __name__ == "__main__":
    compute_top_issues()
