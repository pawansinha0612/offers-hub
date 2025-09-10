import sqlite3

conn = sqlite3.connect("offers.db")  # points to your local DB file
cur = conn.cursor()

cur.execute("SELECT * FROM offers ORDER BY scraped_at DESC ")
rows = cur.fetchall()

print(f"Total offers: {len(rows)}")
for r in rows:
    print(r)

conn.close()
