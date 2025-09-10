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
    Column("store", String(255), unique=True, index=True),
    Column("cashback", String(50)),
    Column("link", Text),
    Column("scraped_at", DateTime, server_default=func.now(), onupdate=func.now()),
)

metadata.create_all(engine)

# --- Flask app ---
app = Flask(__name__)
CORS(app)

# --- DB helpers ---
def save_offers(offers_list):
    with engine.begin() as conn:
        for offer in offers_list:
            stmt = text("""
                INSERT INTO offers (store, cashback, link, scraped_at)
                VALUES (:store, :cashback, :link, NOW())
                ON CONFLICT (store) DO UPDATE
                SET cashback = EXCLUDED.cashback,
                    link = EXCLUDED.link,
                    scraped_at = NOW()
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

# --- Scraper ---
async def scrape_shopback():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"]
        )
        page = await browser.new_page()
        await page.goto("https://www.shopback.com.au/all-stores", timeout=120000)

        prev_count = 0
        while True:
            await page.mouse.wheel(0, 5000)
            try:
                await page.wait_for_function("""
                    () => document.querySelectorAll('div.cursor_pointer.pos_relative').length > arguments[0]
                """, prev_count, timeout=15000)
            except:
                pass
            cards = await page.query_selector_all("div.cursor_pointer.pos_relative")
            print(f"Loaded {len(cards)} store cards")
            if len(cards) == prev_count:
                break
            prev_count = len(cards)

        unique = {}
        for card in cards:
            name = await card.get_attribute("data-merchant-name")
            cashback = await card.get_attribute("data-max-cashback-rate")
            link = await card.get_attribute("data-feature-destination-url")
            if name:
                key = name.strip().lower()
                unique[key] = {
                    "store": name.strip(),
                    "cashback": cashback.strip() if cashback else "N/A",
                    "link": link.strip() if link else "N/A"
                }

        await browser.close()
        return list(unique.values())

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

# --- Verify DB content at startup ---
def check_db():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT store, cashback, link FROM offers LIMIT 5")).fetchall()
        print(f"✅ Database connection successful, sample data:")
        for r in result:
            print(f"Store: {r.store}, Cashback: {r.cashback}, Link: {r.link}")
    except Exception as e:
        print("❌ Database connection failed or no data:", e)

# --- Main ---
if __name__ == "__main__":
    print("Python version:", sys.version)
    check_db()  # Print DB sample at startup

    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
