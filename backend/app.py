# backend/app.py
import os
import sys
import threading
import asyncio
from datetime import datetime
import atexit
import requests

from flask import Flask, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, DateTime, func, select, text
from apscheduler.schedulers.background import BackgroundScheduler
from playwright.async_api import async_playwright

# --- Python version log ---
print("Python version:", sys.version)

# --- Config ---
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    # fallback to SQLite if no DB is configured
    DATABASE_URL = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'offers.db')}"

# Fix scheme if Render gives postgres:// instead of postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQLite-specific args
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, future=True)
metadata = MetaData()

# --- Table definition ---
offers_table = Table(
    "offers",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("store", String(255)),
    Column("cashback", String(50)),
    Column("link", Text),
    Column("scraped_at", DateTime, server_default=func.now()),
)

metadata.create_all(engine)

# --- Flask app ---
app = Flask(__name__)
CORS(app)

# --- DB helpers ---
def save_offers(offers_list):
    with engine.begin() as conn:
        conn.execute(offers_table.delete())
        if offers_list:
            rows = [{"store": o["store"], "cashback": o["cashback"], "link": o["link"]} for o in offers_list]
            conn.execute(offers_table.insert(), rows)

def load_offers():
    with engine.connect() as conn:
        stmt = select(
            offers_table.c.store,
            offers_table.c.cashback,
            offers_table.c.link,
            offers_table.c.scraped_at
        ).order_by(offers_table.c.id)
        rows = conn.execute(stmt).fetchall()
    result = []
    for r in rows:
        scraped_at = r.scraped_at.isoformat() if r.scraped_at else None
        result.append({"store": r.store, "cashback": r.cashback, "link": r.link, "scraped_at": scraped_at})
    return result

# --- Scraper ---
async def scrape_shopback_internal():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-setuid-sandbox"]
        )
        page = await browser.new_page()
        await page.goto("https://www.shopback.com.au/all-stores", timeout=90000)

        # Gentle scrolling
        for _ in range(5):
            await page.mouse.wheel(0, 3000)
            await page.wait_for_timeout(1500)

        cards = await page.query_selector_all("div.cursor_pointer.pos_relative")
        scraped = []
        for card in cards:
            name = await card.get_attribute("data-merchant-name")
            cashback = await card.get_attribute("data-max-cashback-rate")
            link = await card.get_attribute("data-feature-destination-url")
            scraped.append({
                "store": name.strip() if name else "N/A",
                "cashback": cashback.strip() if cashback else "N/A",
                "link": link.strip() if link else "N/A"
            })
        await browser.close()
        return scraped

def run_scrape_and_save_sync():
    try:
        offers = asyncio.run(scrape_shopback_internal())
        save_offers(offers)
        print(f"✅ Scraped {len(offers)} offers and saved to DB")
    except Exception as e:
        print("❌ Scrape failed:", e)

# --- Flask endpoints ---
@app.route("/offers")
def offers():
    return jsonify(load_offers())

@app.route("/scrape-now")
def scrape_now():
    thread = threading.Thread(target=run_scrape_and_save_sync, daemon=True)
    thread.start()
    return jsonify({"status": "Scrape started"}), 202

@app.route("/")
def home():
    return jsonify({"status": "OK", "note": "Visit /offers and /scrape-now"}), 200

# --- Background initial scrape ---
def initial_scrape_background():
    try:
        if not load_offers():
            print("DB empty — starting background initial scrape")
            run_scrape_and_save_sync()
    except Exception as e:
        print("Initial scrape error:", e)

# --- Scheduler ---
scheduler = BackgroundScheduler()

def scheduled_scrape():
    print(f"{datetime.now()}: Scheduled scrape starting...")
    run_scrape_and_save_sync()

scheduler.add_job(func=scheduled_scrape, trigger="interval", hours=6)

def keep_alive_ping():
    backend_url = os.environ.get("BACKEND_URL")
    if not backend_url:
        return
    try:
        requests.get(f"{backend_url}/offers", timeout=10)
        print(f"{datetime.now()}: Keep-alive ping successful")
    except Exception as e:
        print(f"{datetime.now()}: Keep-alive ping failed:", e)

scheduler.add_job(func=keep_alive_ping, trigger="interval", minutes=5)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

# --- Main ---
if __name__ == "__main__":
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Database connection successful")
        threading.Thread(target=initial_scrape_background, daemon=True).start()
    except Exception as e:
        print("❌ Database connection failed:", e)
        print("⚠️ Skipping initial scrape until DB is reachable")

    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
