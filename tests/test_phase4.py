"""
tests/test_phase4.py — Phase 4 Clustering & PM Insight tests.

Exit criteria (from implementation plan):
  ✅ Same input and seed give the same clusters (deterministic UMAP/HDBSCAN).
  ✅ Verifier passes on all stored insights.
"""

import pytest
import numpy as np
import umap
from sklearn.cluster import HDBSCAN
from src.pipeline.cluster import verify_quotes

def test_deterministic_clustering():
    """Test that UMAP + HDBSCAN produces the exact same clusters given the same seed."""
    # Synthetic random embeddings
    np.random.seed(42)
    embeddings = np.random.rand(50, 384)
    
    def run_cluster(embs):
        umap_model = umap.UMAP(n_neighbors=5, n_components=5, metric='cosine', random_state=42)
        reduced = umap_model.fit_transform(embs)
        
        hdbscan_model = HDBSCAN(min_cluster_size=5, min_samples=2)
        labels = hdbscan_model.fit_predict(reduced)
        return labels.tolist()
        
    labels1 = run_cluster(embeddings)
    labels2 = run_cluster(embeddings)
    
    assert labels1 == labels2, "Clustering should be deterministic with a fixed random_state"


def test_quote_verifier():
    """Test the hallucination guardrail checks substring correctly and is case-insensitive."""
    source_texts = [
        "I was trying to find a picture of my dog but the search just crashed. I hate this app.",
        "Couldn't find the receipt from Home Depot. So frustrating."
    ]
    
    # 1. Exact substring
    valid1 = "the search just crashed"
    # 2. Exact substring with different casing
    valid2 = "COULDN'T FIND THE receipt from Home Depot."
    # 3. Hallucinated / slightly changed quote
    invalid1 = "the app just crashed"
    # 4. Partial mismatch
    invalid2 = "Couldn't find my receipt"
    
    quotes = [valid1, valid2, invalid1, invalid2]
    
    verified = verify_quotes(quotes, source_texts)
    
    assert valid1 in verified
    assert valid2 in verified
    assert invalid1 not in verified
    assert invalid2 not in verified
    assert len(verified) == 2
