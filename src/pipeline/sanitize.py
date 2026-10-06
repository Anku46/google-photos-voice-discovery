import re
import hashlib
import uuid
from typing import Dict, Any

def sanitize_text(text: str) -> str:
    """
    Removes PII (emails, phone numbers, URLs, handles) from raw text.
    Note: This regex-based approach does NOT catch real names or physical addresses.
    """
    if not text:
        return ""
    
    # Mask emails
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    text = re.sub(email_pattern, '[EMAIL]', text)
    
    # Mask phone numbers (simplified for international/US)
    phone_pattern = r'(\+\d{1,3}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}'
    text = re.sub(phone_pattern, '[PHONE]', text)
    
    # Mask URLs
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
    text = re.sub(url_pattern, '[URL]', text)
    
    # Mask @handles
    handle_pattern = r'@[a-zA-Z0-9_]+'
    text = re.sub(handle_pattern, '[HANDLE]', text)
    
    return text

def generate_synthetic_id(prefix: str = "rev_") -> str:
    """Generates a random anonymous ID."""
    return f"{prefix}{uuid.uuid4().hex[:8]}"

def generate_hash(text: str) -> str:
    """Generates a SHA-256 hash for deduplication. Normalizes text first."""
    # Normalize: lowercase, strip whitespace, remove punctuation for robust hashing
    normalized = re.sub(r'[^\w\s]', '', text.lower().strip())
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()

def process_raw_review(raw_text: str, source: str, rating: int = None, date=None, app_version=None) -> Dict[str, Any]:
    """Applies privacy guardrails and formats the review for DB ingestion."""
    sanitized_text = sanitize_text(raw_text)
    review_hash = generate_hash(sanitized_text)
    synthetic_id = generate_synthetic_id()
    
    return {
        "review_id": synthetic_id,
        "source": source,
        "review_text": sanitized_text,
        "rating": rating,
        "review_date": date,
        "app_version": app_version,
        "text_hash": review_hash
    }
