from flask import Flask, jsonify
from flask_cors import CORS
import csv
import asyncio
import sys
import os

print("Python version:", sys.version)

from playwright.async_api import async_playwright

app = Flask(__name__)
CORS(app)

CSV_FILE = "shopback_offers.csv"

# Background scraper task
async def scrape_shopback():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto("https://www.shopback.com.au/all-stores", timeout=60000)

        # Scroll to load more offers
        for _ in range(8):
            await page.mouse.wheel(0, 3000)
            await page.wait_for_timeout(2000)

        cards = await page.query_selector_all("div.cursor_pointer.pos_relative")
        scraped = []

        for card in cards:
            name = await card.get_attribute("data-merchant-name")
            cashback = await card.get_attribute("data-max-cashback-rate")
            link = await card.get_attribute("data-feature-destination-url")

            scraped.append([
                name.strip() if name else "N/A",
                cashback.strip() if cashback else "N/A",
                link.strip() if link else "N/A"
            ])

        # Write CSV
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Store", "Cashback (%)", "Link"])
            writer.writerows(scraped)

        await browser.close()
        print(f"✅ Scraped {len(scraped)} offers into {CSV_FILE}")

# Endpoint to get offers
@app.route("/offers")
def offers():
    data = []
    if not os.path.exists(CSV_FILE):
        return jsonify(data)  # Return empty list if CSV doesn't exist
    try:
        with open(CSV_FILE, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
    except Exception as e:
        return {"error": str(e)}, 500
    return jsonify(data)

# Endpoint to scrape now manually
@app.route("/scrape-now")
def scrape_now():
    try:
        asyncio.run(scrape_shopback())
        return {"status": "Scraping finished, CSV updated."}
    except Exception as e:
        return {"error": str(e)}, 500

# Home endpoint
@app.route("/")
def home():
    return "✅ Offers Hub backend is running. Visit /offers to see data."

if __name__ == "__main__":
    # Optional: initial scrape at startup
    if not os.path.exists(CSV_FILE):
        try:
            asyncio.run(scrape_shopback())
        except Exception as e:
            print(f"⚠️ Initial scrape failed: {e}")

    app.run(debug=True, host="0.0.0.0", port=5000)
