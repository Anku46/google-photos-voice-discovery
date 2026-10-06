import time
from typing import List, Dict, Any
from app_store_scraper import AppStore
import os
import sys
import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pipeline.sanitize import process_raw_review
from db import insert_review, get_existing_hashes


class BaseAppStoreScraper:
    """Interface for Apple App Store scraping. Isolates fragile dependencies."""
    def fetch_reviews(self, app_name: str, app_id: int, count: int) -> List[Dict[str, Any]]:
        raise NotImplementedError


class AppStoreScraperLib(BaseAppStoreScraper):
    """Implementation using the app-store-scraper package."""
    def fetch_reviews(self, app_name: str, app_id: int, count: int) -> List[Dict[str, Any]]:
        photos_app = AppStore(country='us', app_name=app_name, app_id=app_id)
        photos_app.review(how_many=count)
        return photos_app.reviews


def scrape_app_store(app_name: str = 'google-photos', app_id: int = 962194608, count: int = 100, scraper: BaseAppStoreScraper = None):
    print(f"Scraping {count} reviews for {app_name} from Apple App Store...")
    
    if scraper is None:
        scraper = AppStoreScraperLib()
        
    existing_hashes = get_existing_hashes()
    
    # Rate limiting & Politeness (Exponential backoff)
    max_retries = 3
    delay = 1
    
    raw_reviews = []
    for attempt in range(max_retries):
        try:
            time.sleep(delay)
            raw_reviews = scraper.fetch_reviews(app_name, app_id, count)
            break
        except Exception as e:
            print(f"Error scraping App Store (Attempt {attempt+1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                return
            delay *= 2
            print(f"Retrying in {delay} seconds...")
            
    inserted = 0
    skipped = 0
    
    for review in raw_reviews:
        processed = process_raw_review(
            raw_text=review.get('review', ''),
            source='app_store',
            rating=review.get('rating'),
            date=review.get('date').strftime("%Y-%m-%d %H:%M:%S") if review.get('date') else None,
            app_version=review.get('developerResponse', {}).get('body')
        )
        
        if not processed['review_text']:
            continue
            
        if processed['text_hash'] in existing_hashes:
            skipped += 1
            continue
            
        success = insert_review(processed)
        if success:
            inserted += 1
            existing_hashes.add(processed['text_hash'])
        else:
            skipped += 1
            
    print(f"App Store: Successfully ingested {inserted} new reviews. Skipped {skipped} duplicates.")

if __name__ == "__main__":
    scrape_app_store()
