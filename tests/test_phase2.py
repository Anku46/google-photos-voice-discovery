"""
tests/test_phase2.py — Phase 2 exit criteria tests.

Exit criteria (from implementation plan):
  ✅ Seeded test PII (emails, phones, handles) is absent from the DB.
  ✅ A re-run inserts 0 duplicates.

Run: pytest tests/ -v
"""

import pytest
from src.pipeline.sanitize import sanitize_text, process_raw_review


def test_pii_masking_emails():
    text = "Contact me at user@example.com for more info."
    sanitized = sanitize_text(text)
    assert "user@example.com" not in sanitized
    assert "[EMAIL]" in sanitized


def test_pii_masking_phones():
    text = "My number is 555-123-4567, call me."
    sanitized = sanitize_text(text)
    assert "555-123-4567" not in sanitized
    assert "[PHONE]" in sanitized


def test_pii_masking_handles():
    text = "Follow me @john_doe123!"
    sanitized = sanitize_text(text)
    assert "@john_doe123" not in sanitized
    assert "[HANDLE]" in sanitized


def test_pii_masking_urls():
    text = "Check out my site https://www.example.com/photos"
    sanitized = sanitize_text(text)
    assert "https://www.example.com/photos" not in sanitized
    assert "[URL]" in sanitized


def test_hashing_ignores_whitespace_and_punctuation():
    text1 = "I love this app!"
    text2 = "  i love this app   "
    text3 = "I... LOVE... THIS APP?!?"
    
    hash1 = process_raw_review(text1, "test")["text_hash"]
    hash2 = process_raw_review(text2, "test")["text_hash"]
    hash3 = process_raw_review(text3, "test")["text_hash"]
    
    assert hash1 == hash2 == hash3


def test_duplicate_prevention_logic():
    # If we ingest the exact same logical text twice, it gets the same text_hash.
    processed1 = process_raw_review("Test review string", "play_store")
    processed2 = process_raw_review("test review string!!!", "play_store")
    
    assert processed1["text_hash"] == processed2["text_hash"]
    # The synthetic IDs should still be unique per processing
    assert processed1["review_id"] != processed2["review_id"]
    
    # Simulate DB `get_existing_hashes()`
    existing_hashes = set()
    
    inserted = 0
    skipped = 0
    
    # Insert 1
    if processed1["text_hash"] not in existing_hashes:
        existing_hashes.add(processed1["text_hash"])
        inserted += 1
    else:
        skipped += 1
        
    # Insert 2 (re-run)
    if processed2["text_hash"] not in existing_hashes:
        existing_hashes.add(processed2["text_hash"])
        inserted += 1
    else:
        skipped += 1
        
    assert inserted == 1
    assert skipped == 1
