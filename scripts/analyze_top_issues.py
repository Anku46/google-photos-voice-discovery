import os
import sys
import sqlite3
import json
from pydantic import BaseModel, Field
from typing import List

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from pipeline.groq_client import get_groq_client
from ingestion.play_store import scrape_play_store

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "discovery_engine.db")

class IssueItem(BaseModel):
    rank: int = Field(description="Rank 1 to 5")
    issue_title: str = Field(description="Short descriptive name of the issue/failure")
    category: str = Field(description="Functional area, e.g. Search & Retrieval, Storage & Backup, UI/Playback, Sync/Locked Folder")
    frequency_and_impact: str = Field(description="How common and severe this issue is among negative reviews")
    root_cause_summary: str = Field(description="Core underlying reason for user frustration")
    representative_quotes: List[str] = Field(description="Direct quotes from the user reviews exhibiting this issue")
    actionable_recommendation: str = Field(description="Product/engineering recommendation to fix or mitigate this issue")

class TopIssuesAnalysis(BaseModel):
    total_reviews_analyzed: int
    top_5_issues: List[IssueItem]
    overall_sentiment_summary: str

def run_analysis():
    # 1. Ensure we have a rich sample of Play Store reviews
    print("Fetching more Play Store reviews to ensure comprehensive dataset...")
    scrape_play_store(count=200)

    # 2. Query all Play Store reviews with rating < 3
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT review_id, rating, review_date, review_text 
        FROM RAW_REVIEWS 
        WHERE source = 'Play Store' AND rating < 3
        ORDER BY review_date DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    print(f"\nFound {len(rows)} Play Store reviews with rating < 3.")
    if not rows:
        print("No low-rating reviews found.")
        return

    # Prepare formatted review corpus
    review_corpus = []
    for r in rows:
        review_corpus.append(f"[{r[0]} | Rating: {r[1]}/5 | Date: {r[2]}] {r[3]}")

    corpus_text = "\n".join(review_corpus)

    # 3. Call Groq LLM (llama-3.3-70b-versatile) via Instructor
    client = get_groq_client()
    
    prompt = f"""
You are a Principal Product Manager & User Experience Analyst at Google analyzing negative user feedback (ratings 1 and 2) for Google Photos from the Play Store.

Review dataset ({len(rows)} reviews with rating < 3):
---
{corpus_text}
---

Your task:
Analyze these negative reviews and identify the TOP 5 most significant user issues / pain points.
For each issue, extract:
1. Rank (1 to 5)
2. Issue Title
3. Category (e.g. Memory & Search Retrieval, Storage / Deletion Policy, Video Playback / Update Glitches, Sync / Locked Folder loss, UI Confusion)
4. Frequency & Impact assessment
5. Root cause summary
6. Representative direct quotes from the reviews
7. Actionable recommendation for Google Photos product team

Return the structured response strictly matching the schema.
"""

    print("Analyzing low-rating reviews with Groq LLM (openai/gpt-oss-120b)...")
    response: TopIssuesAnalysis = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        response_model=TopIssuesAnalysis,
        messages=[
            {"role": "system", "content": "You are an expert AI product analyst specialized in user feedback clustering and failure diagnosis. Keep summaries concise and quotes under 20 words each."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        max_tokens=4096
    )

    # Save output to a JSON artifact for reporting
    output_path = os.path.join(os.path.dirname(__file__), "..", "data", "top5_issues_analysis.json")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(response.model_dump_json(indent=2))
    print(f"\nAnalysis saved to {output_path}")

    print("\n" + "="*80)
    print("TOP 5 PREDICTED ISSUES (PLAY STORE REVIEWS RATING < 3)")
    print("="*80)
    print(f"Total Low-Rating Reviews Analyzed: {response.total_reviews_analyzed}")
    print(f"Overall Summary: {response.overall_sentiment_summary.encode('ascii', 'ignore').decode('ascii')}\n")

    for issue in response.top_5_issues:
        print(f"#{issue.rank}. {issue.issue_title.upper()} [{issue.category}]")
        print(f"  Impact: {issue.frequency_and_impact.encode('ascii', 'ignore').decode('ascii')}")
        print(f"  Root Cause: {issue.root_cause_summary.encode('ascii', 'ignore').decode('ascii')}")
        print("  Quotes:")
        for q in issue.representative_quotes:
            print(f"    - \"{q.encode('ascii', 'ignore').decode('ascii')}\"")
        print(f"  Recommendation: {issue.actionable_recommendation.encode('ascii', 'ignore').decode('ascii')}")
        print("-" * 80)

if __name__ == "__main__":
    run_analysis()
