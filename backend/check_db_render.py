import os
from sqlalchemy import create_engine, text

# Replace with your Render DB URL
DATABASE_URL = "postgresql://offershubdb_user:rm6uWbORjTiGel31Jl8o6wC2UpqMibMw@dpg-d2uhgr3e5dus73eoks40-a.oregon-postgres.render.com/offershubdb"

# Make sure SSL is required
engine = create_engine(DATABASE_URL, connect_args={"sslmode": "require"}, pool_pre_ping=True, future=True)

try:
    with engine.connect() as conn:
        # Quick connectivity test
        result = conn.execute(text("SELECT 1"))
        print("✅ Database connection successful:", result.scalar())

        # Count rows in offers table
        count = conn.execute(text("SELECT COUNT(*) FROM offers")).scalar()
        print(f"Total rows in offers table: {count}")

        # Show 5 latest entries
        rows = conn.execute(text("SELECT store, cashback, link, scraped_at FROM offers ORDER BY scraped_at DESC LIMIT 5")).fetchall()
        for r in rows:
            print(r)

except Exception as e:
    print("❌ Database connection failed:", e)
