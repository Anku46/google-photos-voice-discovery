import time
import httpx
import os
import sys
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pipeline.sanitize import process_raw_review
from db import insert_review, get_existing_hashes

def scrape_reddit(subreddit: str = 'googlephotos', limit: int = 100):
    print(f"Scraping {limit} posts from r/{subreddit} on Reddit...")
    
    url = f"https://www.reddit.com/r/{subreddit}/new.json?limit={limit}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    # Incremental Ingestion: skip existing
    existing_hashes = get_existing_hashes()
    
    # Rate limiting & Politeness (Exponential backoff)
    max_retries = 3
    delay = 1
    
    data = {}
    for attempt in range(max_retries):
        try:
            time.sleep(delay)
            response = httpx.get(url, headers=headers)
            if response.status_code == 429 or response.status_code >= 500:
                print(f"Rate limited or server error ({response.status_code}).")
                if attempt == max_retries - 1:
                    return
                delay *= 2
                print(f"Retrying in {delay} seconds...")
                continue
                
            if response.status_code != 200:
                print(f"Failed to fetch Reddit data. Status Code: {response.status_code}")
                return
                
            data = response.json()
            break
        except Exception as e:
            print(f"Error scraping Reddit (Attempt {attempt+1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                return
            delay *= 2
            print(f"Retrying in {delay} seconds...")
            
    posts = data.get('data', {}).get('children', [])
    
    inserted = 0
    skipped = 0
    
    for post in posts:
        post_data = post['data']
        # Combine title and body to form the "review" text
        title = post_data.get('title', '')
        body = post_data.get('selftext', '')
        full_text = f"{title}\n\n{body}".strip()
        
        if not full_text:
            continue
            
        timestamp = post_data.get('created_utc')
        date_str = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S') if timestamp else None
        
        processed = process_raw_review(
            raw_text=full_text,
            source='reddit',
            rating=None, # Reddit doesn't have ratings
            date=date_str,
            app_version=None
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
            
    print(f"Reddit: Successfully ingested {inserted} new posts. Skipped {skipped} duplicates.")

if __name__ == "__main__":
    scrape_reddit()
