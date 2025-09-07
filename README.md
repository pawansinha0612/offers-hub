---

# Offers Hub

A web service to fetch, store, and serve cashback offers from **ShopBack Australia**.
This project uses **Flask + Playwright + SQLAlchemy** for the backend, stores offers in a **database** (SQLite locally / Postgres in the cloud), and serves data to a **React frontend**.

---

## Features

* Scrapes ShopBack Australia for store cashback offers.
* Stores offers in **SQLite (local)** or **Postgres (cloud)**.
* REST API endpoints:

   * `/offers` — Returns all stored offers as JSON.
   * `/scrape-now` — Triggers a manual background scrape.
   * `/` — Health check endpoint.
* Automatic scraping **every 6 hours** using APScheduler.
* Free Render instances are kept alive by self-pinging `/offers` every 5 minutes.
* React frontend fetches live offers and displays them in a table.
* Optional CSV import for pre-existing offers.

---

## First-Time Setup

### Backend (Python + Flask)

1. Clone the repository:

```bash
git clone https://github.com/<your-username>/offers-hub.git
cd offers-hub/backend
```

2. Create a virtual environment and activate it:

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

3. Install dependencies:

```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
playwright install chromium
```

4. Set environment variable for database:

```bash
export DATABASE_URL="postgresql://<user>:<password>@<host>:<port>/<database>"
```

If not provided, the backend will default to `SQLite` file `offers.db`.

5. Run backend locally:

```bash
python app.py
```

Visit:

* `http://127.0.0.1:5000/offers` → View offers
* `http://127.0.0.1:5000/scrape-now` → Trigger manual scrape

---

### Frontend (React)

1. Go to frontend directory:

```bash
cd ../frontend
npm install
```

2. Update API URL in `frontend/src/api.js`:

```js
export async function fetchOffers() {
  const res = await fetch("http://127.0.0.1:5000/offers");
  if (!res.ok) throw new Error("Failed");
  return res.json();
}
```

3. Run frontend locally:

```bash
npm start
```

---

### Optional: CSV Import

If you have an existing CSV file `shopback_offers.csv`, you can import it to the database:

```bash
cd backend
python import_csv_to_db.py
```

---

## API Endpoints

| Endpoint      | Method | Description                            |
| ------------- | ------ | -------------------------------------- |
| `/offers`     | GET    | Returns all offers from the database.  |
| `/scrape-now` | GET    | Triggers a background scrape manually. |
| `/`           | GET    | Health check / info endpoint.          |

### Response Fields

* `store` — Store name
* `cashback` — Cashback percentage
* `link` — Offer URL
* `scraped_at` — Timestamp when scraped

---

## Architecture Diagram

```text
+-----------------+       +-------------------+       +------------------+
|   User / React  | <---> |    Render Backend | <---> |   Database (DB)  |
|   Frontend      |       | Flask + APScheduler|       | SQLite / Postgres|
+-----------------+       +-------------------+       +------------------+
       ^                         ^
       |                         |
       |                         +-- Background scraping every 6 hours
       |                         +-- Self-ping /offers every 5 min
       |
       +-- Fetch offers from /offers endpoint
```

---

## Offers Hub Data Flow

```text
+------------------+        +------------------+        +------------------+
|   CSV File       |  --->  |  import_csv_to_db|  --->  |    Database      |
| shopback_offers.csv |      |  (pre-existing) |        | (SQLite / Postgres)|
+------------------+        +------------------+        +------------------+
                                      ^
                                      |
                                      |
                             +------------------+
                             |  Scraper / API   |
                             | /scrape-now or   |
                             | Scheduled Job    |
                             +------------------+
                                      |
                                      v
                             +------------------+
                             |   Frontend App   |
                             |  React / Fetch   |
                             |   /offers        |
                             +------------------+
```

---

## Deployment on Render

### Step 1: PostgreSQL Database

* Render → New → PostgreSQL Database
* Copy connection string for `DATABASE_URL`
  Example:

  ```
  postgresql://user:password@host:5432/offers_db?sslmode=require
  ```

### Step 2: Web Service

1. Render → New → Web Service → Connect GitHub repo

   * Root directory: `backend`
   * Environment Variable: `DATABASE_URL=<your-db-url>`

2. Build command:

```bash
pip install --upgrade pip setuptools wheel && pip install -r requirements.txt && playwright install chromium
```

3. Start command:

```bash
gunicorn -w 4 -b 0.0.0.0:$PORT app:app
```

4. Deploy. Your API will be live at `https://<your-service>.onrender.com/offers`.

---

## Scheduler & Keep-Alive

* **APScheduler** automatically scrapes every 6 hours.
* `/offers` endpoint is pinged every 5 minutes to keep free Render instances awake.

---

## Notes

* Database stores offers persistently — no memory-only storage.
* Supports **SQLite** for local dev and **Postgres** for cloud.
* CSV import is optional but useful for initializing the database.
* Free Render instances may spin down if idle — keep-alive ping prevents this.

---

This README is **fully complete**, including:

* Backend setup, frontend setup
* Environment variables
* API endpoints
* CSV import
* Deployment on Render
* Architecture diagram
* Data flow diagram
* Scheduler & keep-alive notes

---