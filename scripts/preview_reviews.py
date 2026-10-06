import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "discovery_engine.db")

def preview():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM raw_reviews")
    count = cursor.fetchone()[0]
    print(f"Total reviews in database: {count}")
    
    cursor.execute("SELECT review_id, source, rating, review_date, review_text FROM raw_reviews LIMIT 6")
    rows = cursor.fetchall()
    print("\n--- SAMPLE SCRAPED & SANITIZED REVIEWS ---")
    for r in rows:
        print(f"\n[ID: {r[0]}] | Source: {r[1]} | Rating: {r[2]}/5 | Date: {r[3]}")
        print(f"Text: \"{r[4]}\"")
    conn.close()

if __name__ == "__main__":
    preview()
