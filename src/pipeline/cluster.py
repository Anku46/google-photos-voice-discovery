"""
pipeline/cluster.py — Stage 6 & 7: Clustering and PM Insight Synthesis (Phase 4).
"""

import os
import uuid
import json
import random
import numpy as np
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from sentence_transformers import SentenceTransformer
import umap
from sklearn.cluster import HDBSCAN
from tenacity import retry, wait_exponential, stop_after_attempt

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pipeline.groq_client import get_groq_client, get_model, check_budget
from pipeline.models import PMInsight, ClusterArchetype
from db import get_client

# ---------------------------------------------------------------------------
# Stage 7: Synthesis and Verifier
# ---------------------------------------------------------------------------

@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(5))
def run_synthesis(client, samples: list[str], size: int, gap_mix: str) -> tuple[ClusterArchetype, PMInsight]:
    """Generates PM insight from 5-10 representative samples."""
    check_budget()
    model = get_model("SYNTHESIZE")
    
    context = "\n---\n".join(samples)
    
    prompt = f"""
    Analyze the following cluster of user feedback from Google Photos.
    Cluster Size: {size} reviews.
    Primary Gaps present in this cluster: {gap_mix}.
    
    Representative Samples:
    {context}
    
    Task 1: Generate a short, descriptive theme title and identify the dominant failure gap.
    Task 2: Synthesize a PM-ready insight (user situation, behavior, root cause, opportunity).
    Task 3: Select EXACT quotes from the samples to back up your insight. 
    
    IMPORTANT: Every quote you select MUST be a verbatim substring of the provided samples. Do not alter capitalization, punctuation, or grammar.
    """
    
    archetype = client.chat.completions.create(
        model=model,
        response_model=ClusterArchetype,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )
    
    insight = client.chat.completions.create(
        model=model,
        response_model=PMInsight,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )
    
    return archetype, insight


def verify_quotes(quotes: list[str], source_texts: list[str]) -> list[str]:
    """
    Hallucination Guardrail: 
    Checks if quotes are exact substrings of the sanitized source texts.
    (Retry logic is handled via tenacity on run_synthesis if we wanted a full loop, 
    but here we implement the 'drop field' strategy for Phase 4.4c).
    """
    valid = []
    source_lower = [s.lower() for s in source_texts]
    for q in quotes:
        q_clean = q.lower().strip()
        if any(q_clean in s for s in source_lower):
            valid.append(q)
        else:
            print(f"GUARDRAIL: Dropped hallucinated/modified quote -> {q}")
    return valid

# ---------------------------------------------------------------------------
# Stage 6: Clustering Pipeline
# ---------------------------------------------------------------------------

def run_clustering():
    db = get_client()
    
    # 1. Fetch relevant, English data from DB
    # Join REVIEWS, FILTERED_REVIEWS, RETRIEVAL_EXPERIENCES, FAILURE_CLASSIFICATIONS
    # This requires a few queries since we don't have a view setup.
    
    rev_resp = db.table("REVIEWS").select("review_id, review_text, review_date, language").eq("language", "en").execute()
    rev_map = {r["review_id"]: r for r in rev_resp.data}
    
    # Only RELEVANT filter
    flt_resp = db.table("FILTERED_REVIEWS").select("review_id").eq("classification", "RETRIEVAL_EXPERIENCE").execute()
    relevant_ids = {r["review_id"] for r in flt_resp.data}
    
    ext_resp = db.table("RETRIEVAL_EXPERIENCES").select("*").execute()
    ext_map = {r["review_id"]: r for r in ext_resp.data if r["review_id"] in relevant_ids}
    
    cls_resp = db.table("FAILURE_CLASSIFICATIONS").select("*").execute()
    # map experience_id -> classification
    cls_map = {r["experience_id"]: r for r in cls_resp.data}
    
    records = []
    for rid, ext in ext_map.items():
        r = rev_map.get(rid)
        if not r: continue
        
        eid = ext["experience_id"]
        c = cls_map.get(eid)
        if not c: continue
        
        records.append({
            "review_id": rid,
            "text": r["review_text"],
            "date": r["review_date"],
            "target": ext.get("target_entity", ""),
            "clues": json.dumps(ext.get("memory_clues", {})),
            "search": ext.get("search_attempt", ""),
            "primary_gap": c.get("primary_gap", "")
        })
        
    if len(records) < 10:
        print("Not enough fully processed English records to cluster (need >= 10).")
        return
        
    print(f"Clustering {len(records)} records...")
    
    # 2. Build semantic string (NO GAP LABEL)
    semantic_strings = []
    for r in records:
        excerpt = r["text"][:200]
        s = f"Target: {r['target']} | Clues: {r['clues']} | Search: {r['search']} | Excerpt: {excerpt}"
        semantic_strings.append(s)
        
    # 3. Generate Embeddings (CPU)
    print("Generating embeddings using sentence-transformers (all-MiniLM-L6-v2)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(semantic_strings, show_progress_bar=True)
    
    # 4. UMAP Reduction
    print("Reducing dimensions with UMAP...")
    n_neighbors = min(15, len(embeddings) - 1)
    umap_model = umap.UMAP(n_neighbors=n_neighbors, n_components=5, metric='cosine', random_state=42)
    reduced_embeddings = umap_model.fit_transform(embeddings)
    
    # 5. HDBSCAN Clustering
    print("Clustering with sklearn HDBSCAN...")
    hdbscan_model = HDBSCAN(min_cluster_size=min(5, len(embeddings)//4), min_samples=2)
    labels = hdbscan_model.fit_predict(reduced_embeddings)
    
    # Group by cluster
    cluster_map = {}
    for i, c_id in enumerate(labels):
        cluster_map.setdefault(c_id, []).append((records[i], reduced_embeddings[i], semantic_strings[i]))
        
    noise_count = len(cluster_map.get(-1, []))
    print(f"Found {len(cluster_map) - (1 if -1 in cluster_map else 0)} dense clusters. Noise points (Unclustered): {noise_count}")
    
    client = get_groq_client()
    
    # Current date for recency calculation (6 months)
    six_months_ago = datetime.now() - relativedelta(months=6)
    
    # Process clusters
    for c_id, members in cluster_map.items():
        is_noise = (c_id == -1)
        cluster_uuid = f"clu_{uuid.uuid4().hex[:8]}"
        
        # Calculate dates
        dates = []
        for m in members:
            d_str = m[0]["date"]
            if d_str:
                try:
                    # Handle different iso formats
                    d_clean = d_str.replace("Z", "+00:00")
                    dates.append(datetime.fromisoformat(d_clean))
                except ValueError:
                    pass
                    
        date_start = min(dates).date().isoformat() if dates else None
        date_end = max(dates).date().isoformat() if dates else None
        recent_count = sum(1 for d in dates if d.replace(tzinfo=None) >= six_months_ago)
        recent_share = recent_count / len(members) if members else 0.0
        
        prevalence = len(members) / len(records)
        gap_mix = ", ".join(list(set([m[0]["primary_gap"] for m in members])))
        
        if is_noise:
            # Just save the Unclustered bucket, no LLM synthesis
            db.table("THEMATIC_CLUSTERS").insert({
                "cluster_id": cluster_uuid,
                "cluster_title": "Unclustered (Noise)",
                "cluster_description": "Reviews that did not form a dense behavioral pattern.",
                "review_count": len(members),
                "prevalence_rate": prevalence,
                "primary_failure_gap": None,
                "date_range_start": date_start,
                "date_range_end": date_end,
                "recent_share": recent_share,
                "is_noise_bucket": True
            }).execute()
            print("Saved Unclustered (Noise) bucket.")
            continue
            
        print(f"\nProcessing Cluster {c_id} ({len(members)} reviews)...")
        
        # Medoids + Spread Selection
        vectors = np.array([m[1] for m in members])
        centroid = np.mean(vectors, axis=0)
        distances = np.linalg.norm(vectors - centroid, axis=1)
        
        # Get up to 5 closest to centroid
        medoid_indices = np.argsort(distances)[:5].tolist()
        
        # Add up to 3 random spread points if cluster is large
        spread_indices = []
        if len(members) > 8:
            available = [i for i in range(len(members)) if i not in medoid_indices]
            spread_indices = random.sample(available, min(3, len(available)))
            
        selected_indices = medoid_indices + spread_indices
        selected_texts = [members[i][0]["text"] for i in selected_indices]
        
        try:
            archetype, insight = run_synthesis(client, selected_texts, len(members), gap_mix)
            
            # Guardrail Verifier
            insight.representative_quotes = verify_quotes(insight.representative_quotes, selected_texts)
            
            # Save to DB
            db.table("THEMATIC_CLUSTERS").insert({
                "cluster_id": cluster_uuid,
                "cluster_title": archetype.theme_title,
                "cluster_description": insight.likely_underlying_problem,
                "review_count": len(members),
                "prevalence_rate": prevalence,
                "primary_failure_gap": archetype.primary_failure_gap.value,
                "date_range_start": date_start,
                "date_range_end": date_end,
                "recent_share": recent_share,
                "is_noise_bucket": False
            }).execute()
            
            insight_uuid = f"ins_{uuid.uuid4().hex[:8]}"
            db.table("PM_INSIGHTS").insert({
                "insight_id": insight_uuid,
                "cluster_id": cluster_uuid,
                "user_situation": insight.user_situation,
                "observed_behavior": insight.observed_behavior,
                "retrieval_failure": insight.retrieval_failure,
                "likely_underlying_problem": insight.likely_underlying_problem,
                "representative_quotes": json.dumps(insight.representative_quotes),
                "potential_opportunity": insight.potential_opportunity
            }).execute()
            
            print(f"Saved Cluster: {archetype.theme_title}")
            
        except Exception as e:
            print(f"Error synthesizing cluster {c_id}: {e}")

    print("\nClustering and Synthesis phase complete.")

if __name__ == "__main__":
    run_clustering()
