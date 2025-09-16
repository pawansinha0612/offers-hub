import sys
import os
import asyncio
import json
from flask import Flask, jsonify

# Add project root to path so we can import scripts.scrape_offers
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from scripts.scrape_offers import scrape_shopback, FRONTEND_JSON_PATH

app = Flask(__name__)

# --- Root endpoint ---
@app.get("/api/")
def home():
    return {"status": "OK", "note": "Use /api/scrape-offers to trigger scraping or /api/offers to view current offers"}

# --- Return current offers.json ---
@app.get("/api/offers")
def offers():
    if os.path.exists(FRONTEND_JSON_PATH):
        with open(FRONTEND_JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {"offers": data}
    else:
        return {"offers": [], "note": "No offers scraped yet"}

# --- Trigger scraper ---
@app.get("/api/scrape-offers")
def scrape_offers_api():
    try:
        offers = asyncio.run(scrape_shopback())

        os.makedirs(os.path.dirname(FRONTEND_JSON_PATH), exist_ok=True)
        with open(FRONTEND_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(offers, f, indent=2)

        print(f"✅ Total offers scraped: {len(offers)}")  # Logs for Vercel
        return jsonify({
            "status": "Scrape completed",
            "total_offers": len(offers)
        }), 200

    except Exception as e:
        print(f"❌ Scrape failed: {e}")
        return jsonify({"status": "Scrape failed", "error": str(e)}), 500

# --- Local test runner ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
