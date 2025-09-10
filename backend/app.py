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
from sqlalchemy.exc import ProgrammingError
from apscheduler.schedulers.background import BackgroundScheduler
from playwright.async_api import async_playwright
from sqlalchemy import inspect

print("Python version:", sys.version)

# --- Config ---
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'offers.db')}"

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# --- SQLAlchemy Engine ---
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    connect_args = {"sslmode": "require"}

engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True, future=True)
metadata = MetaData()

# --- Table definition ---
offers_table = Table(
    "offers",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("store", String(255)),
    Column("cashback", String(50)),
    Column("link", Text),
    Column("scraped_at", DateTime, server_default=func.now(), onupdate=func.now()),
)

# --- Schema Initialization ---
def initialize_schema():
    with engine.connect() as conn:
        try:
            # Drop the table if it exists
            conn.execute(text("DROP TABLE IF EXISTS offers"))
            conn.commit()
            # Recreate the table
            metadata.create_all(engine)
            print("✅ Table 'offers' dropped and recreated successfully")
        except Exception as e:
            print(f"❌ Error during table drop/recreate: {e}")
            conn.rollback()
            raise

# Run schema initialization on module import
initialize_schema()

# --- Flask app ---
app = Flask(__name__)
CORS(app)

# --- DB helpers ---
def save_offers(offers_list):
    with engine.begin() as conn:
        if engine.dialect.name == "sqlite":
            timestamp_func = "CURRENT_TIMESTAMP"
        else:
            timestamp_func = "NOW()"

        for offer in offers_list:
            stmt = text(f"""
                INSERT INTO offers (store, cashback, link, scraped_at)
                VALUES (:store, :cashback, :link, {timestamp_func})
            """)
            conn.execute(stmt, offer)

def load_offers():
    with engine.connect() as conn:
        stmt = select(
            offers_table.c.store,
            offers_table.c.cashback,
            offers_table.c.link,
            offers_table.c.scraped_at
        ).order_by(offers_table.c.store.asc())
        rows = conn.execute(stmt).fetchall()
    result = []
    for r in rows:
        scraped_at = r.scraped_at.isoformat() if r.scraped_at else None
        result.append({
            "store": r.store,
            "cashback": r.cashback,
            "link": r.link,
            "scraped_at": scraped_at
        })
    return result

async def scrape_shopback():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"]
        )
        page = await browser.new_page()
        await page.goto("https://www.shopback.com.au/all-stores", timeout=180000)

        # --- Scroll until all offers are loaded ---
        prev_count = 0
        stable_scrolls = 0
        while True:
            await page.mouse.wheel(0, 1000)
            await asyncio.sleep(1.5)

            cards = await page.query_selector_all("div.cursor_pointer.pos_relative")
            if len(cards) == prev_count:
                stable_scrolls += 1
            else:
                stable_scrolls = 0

            if stable_scrolls >= 3:
                break

            prev_count = len(cards)
            print(f"Loaded {len(cards)} store cards so far...")

        # --- Collect all offers ---
        offers_list = []
        for card in cards:
            name = await card.get_attribute("data-merchant-name")
            cashback = await card.get_attribute("data-max-cashback-rate")
            link = await card.get_attribute("data-feature-destination-url")
            if name:
                offers_list.append({
                    "store": name.strip(),
                    "cashback": cashback.strip() if cashback else "N/A",
                    "link": link.strip() if link else "N/A"
                })

        await browser.close()
        print(f"✅ Total offers scraped: {len(offers_list)}")
        return offers_list

def run_scrape_sync():
    try:
        offers = asyncio.run(scrape_shopback())
        save_offers(offers)
        print(f"✅ Scraped {len(offers)} unique offers and saved")
    except Exception as e:
        print("❌ Scrape failed:", e)

# --- Flask endpoints ---
@app.route("/offers")
def offers():
    return jsonify(load_offers())

@app.route("/scrape-now")
def scrape_now():
    thread = threading.Thread(target=run_scrape_sync, daemon=True)
    thread.start()
    return jsonify({"status": "Scrape started"}), 202

@app.route("/")
def home():
    return jsonify({"status": "OK", "note": "Visit /offers and /scrape-now"}), 200

# --- Scheduler ---
scheduler = BackgroundScheduler()

def scheduled_scrape():
    print(f"{datetime.now()}: Scheduled scrape starting...")
    run_scrape_sync()

scheduler.add_job(func=scheduled_scrape, trigger="interval", hours=6)

def keep_alive_ping():
    backend_url = os.environ.get("BACKEND_URL")
    if backend_url:
        try:
            requests.get(f"{backend_url}/offers", timeout=10)
            print(f"{datetime.now()}: Keep-alive ping successful")
        except Exception as e:
            print(f"{datetime.now()}: Keep-alive ping failed:", e)

scheduler.add_job(func=keep_alive_ping, trigger="interval", minutes=5)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

if __name__ == "__main__":
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Database connection successful (main block)")

        # First synchronous scrape to populate /offers immediately
        run_scrape_sync()

    except Exception as e:
        print("❌ Database connection failed:", e)

    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)