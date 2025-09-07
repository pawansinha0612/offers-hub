# backend/import_csv_to_db.py
import csv, os, sqlite3
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, DateTime, func, insert

DATABASE_URL = os.environ.get("DATABASE_URL") or f"sqlite:///{os.path.join(os.path.dirname(__file__), 'offers.db')}"
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, DateTime, func
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})

metadata = MetaData()
offers_table = Table(
    "offers", metadata,
    Column("id", Integer, primary_key=True),
    Column("store", String(255)),
    Column("cashback", String(50)),
    Column("link", Text),
    Column("scraped_at", DateTime, server_default=func.now()),
)
metadata.create_all(engine)

csv_path = os.path.join(os.path.dirname(__file__), "shopback_offers.csv")
rows = []
with open(csv_path, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append({"store": r.get("Store"), "cashback": r.get("Cashback (%)") or r.get("New User Cashback") or r.get("Cashback"), "link": r.get("Link")})

with engine.begin() as conn:
    conn.execute(offers_table.delete())
    if rows:
        conn.execute(offers_table.insert(), rows)
print("Imported", len(rows), "rows")
