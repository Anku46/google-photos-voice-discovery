"""
pipeline/copilot.py — Phase 5.5 Copilot Design
In-memory cosine-similarity search and SQL aggregate routing.
"""

import numpy as np
from sentence_transformers import SentenceTransformer
import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from db import get_client
from pipeline.groq_client import get_groq_client, get_model

# Load model once for in-memory RAG
_embed_model = None

def get_embed_model():
    global _embed_model
    if _embed_model is None:
        _embed_model = SentenceTransformer('all-MiniLM-L6-v2')
    return _embed_model


def _fetch_reviews_context():
    """Fetch sanitized text and metadata for RAG."""
    db = get_client()
    resp = db.table("REVIEWS").select("review_id, review_text, rating").execute()
    return resp.data


def retrieve_relevant_reviews(query: str, top_k: int = 5) -> list[dict]:
    """In-memory cosine similarity search for reviews matching the user query."""
    reviews = _fetch_reviews_context()
    if not reviews:
        return []
        
    texts = [r["review_text"] for r in reviews]
    
    model = get_embed_model()
    query_emb = model.encode([query])[0]
    doc_embs = model.encode(texts)
    
    # Cosine similarity
    similarities = np.dot(doc_embs, query_emb) / (np.linalg.norm(doc_embs, axis=1) * np.linalg.norm(query_emb))
    
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    
    return [reviews[i] for i in top_indices]


def answer_copilot_query(query: str) -> str:
    """Answers a Copilot query using retrieved context."""
    # 1. Check if it's an aggregate query
    lower_q = query.lower()
    db = get_client()
    aggregate_context = ""
    
    if any(kw in lower_q for kw in ["how many", "count", "percentage", "total"]):
        # Fetch some basic aggregates
        total_revs = db.table("REVIEWS").select("review_id", count="exact").execute().count
        agg_str = f"Total reviews: {total_revs}\n"
        
        # Get gap counts
        cls = db.table("FAILURE_CLASSIFICATIONS").select("primary_gap").execute()
        from collections import Counter
        gaps = Counter([r["primary_gap"] for r in cls.data])
        agg_str += f"Gap Distribution: {json.dumps(dict(gaps))}\n"
        
        aggregate_context = agg_str
        
    # 2. Retrieve specific reviews
    relevant_reviews = retrieve_relevant_reviews(query)
    review_context = "\n".join([f"[ID: {r['review_id']}] {r['review_text']} (Rating: {r['rating']})" for r in relevant_reviews])
    
    prompt = f"""
    You are an AI product assistant analyzing user feedback.
    
    Context Data:
    {aggregate_context}
    
    Relevant Reviews:
    {review_context}
    
    User Question: {query}
    
    Instructions:
    1. Answer the user's question using ONLY the context provided above.
    2. If the data cannot answer the question, say "I cannot answer this based on the available data."
    3. If quoting a review, include the exact substring and cite the [ID].
    4. Do not hallucinate numbers. Use the aggregate data if provided.
    """
    
    client = get_groq_client()
    model = get_model("SYNTHESIZE") # Reuse synthesize model
    
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content
