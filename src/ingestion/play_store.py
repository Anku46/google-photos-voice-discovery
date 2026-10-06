import time
from google_play_scraper import Sort, reviews
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pipeline.sanitize import process_raw_review
from db import insert_review, get_existing_hashes

def scrape_play_store(app_id: str = 'com.google.android.apps.photos', count: int = 100):
    print(f"Scraping {count} reviews for {app_id} from Google Play Store...")
    
    # Incremental Ingestion: skip existing
    existing_hashes = get_existing_hashes()
    
    # Rate limiting & Politeness (Exponential backoff)
    max_retries = 3
    delay = 1
    
    for attempt in range(max_retries):
        try:
            time.sleep(delay)
            result, continuation_token = reviews(
                app_id,
                lang='en',
                country='us',
                sort=Sort.NEWEST,
                count=count
            )
            break
        except Exception as e:
            print(f"Error scraping Play Store (Attempt {attempt+1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                return
            delay *= 2
            print(f"Retrying in {delay} seconds...")
            
    
    inserted = 0
    skipped = 0
    
    for review in result:
        processed = process_raw_review(
            raw_text=review['content'],
            source='play_store',
            rating=review['score'],
            date=review['at'].strftime("%Y-%m-%d %H:%M:%S") if review['at'] else None,
            app_version=review['reviewCreatedVersion']
        )
        
        if processed['text_hash'] in existing_hashes:
            skipped += 1
            continue
            
        success = insert_review(processed)
        if success:
            inserted += 1
            existing_hashes.add(processed['text_hash'])
        else:
            skipped += 1
            
    print(f"Play Store: Successfully ingested {inserted} new reviews. Skipped {skipped} duplicates.")

if __name__ == "__main__":
    scrape_play_store()
