import sqlite3
conn = sqlite3.connect('data/discovery_engine.db')
c = conn.cursor()
tables = ['RAW_REVIEWS','FILTERED_REVIEWS','RETRIEVAL_EXPERIENCES','FAILURE_CLASSIFICATIONS','THEMATIC_CLUSTERS','PM_INSIGHTS']
for t in tables:
    count = c.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
    print(f"{t}: {count}")
conn.close()
