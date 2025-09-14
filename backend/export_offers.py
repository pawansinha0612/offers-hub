import sqlite3
import json

def export_to_json(db_path="offers.db", json_path="../frontend/src/offers.json"):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Pull all rows
        cursor.execute("SELECT id, store, cashback, link, scraped_at FROM offers")
        rows = cursor.fetchall()

        # Convert to list of dicts
        offers = []
        for row in rows:
            offers.append({
                "id": row[0],
                "store": row[1],
                "cashback": row[2],
                "link": row[3],
                "scraped_at": row[4]
            })

        # Write JSON file
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(offers, f, indent=2, ensure_ascii=False)

        print(f"✅ Exported {len(offers)} offers to {json_path}")

    except Exception as e:
        print(f"❌ Export failed: {e}")

    finally:
        conn.close()


if __name__ == "__main__":
    export_to_json()
