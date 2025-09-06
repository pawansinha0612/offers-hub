import asyncio
import csv
from flask import Flask, jsonify
from flask_cors import CORS
from playwright.async_api import async_playwright
import os

app = Flask(__name__)
CORS(app)

CSV_FILE = os.path.join(os.path.dirname(__file__), "shopback_offers.csv")


# --- Playwright scraper (your code, wrapped) ---
async def scrape_shopback():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # headless for Render
        page = await browser.new_page()

        await page.goto("https://www.shopback.com.au/all-stores", timeout=60000)

        # Scroll to load more offers
        for _ in range(8):
            await page.mouse.wheel(0, 3000)
            await page.wait_for_timeout(2000)

        # Grab merchant cards
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

        await browser.close()

        # Save to CSV
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Store", "Cashback (%)", "Link"])
            writer.writerows(scraped)

        print(f"✅ Scraped {len(scraped)} offers into {CSV_FILE}")
        return scraped


def read_offers_from_csv():
    offers = []
    if not os.path.exists(CSV_FILE):
        return offers
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            offers.append(row)
    return offers


@app.route("/offers", methods=["GET"])
def get_offers():
    try:
        # Try live scrape
        offers = asyncio.run(scrape_shopback())
        return jsonify([
            {"Store": o[0], "Cashback (%)": o[1], "Link": o[2]}
            for o in offers
        ])
    except Exception as e:
        print(f"❌ Scrape failed: {e}. Falling back to CSV.")
        # Fallback to last saved CSV
        return jsonify(read_offers_from_csv())


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
