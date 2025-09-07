---

# Offers Hub

A web service to fetch, store, and serve cashback offers from ShopBack Australia.
This project uses **Flask + Playwright + SQLAlchemy** for the backend, stores offers in a **database** (SQLite locally / Postgres in the cloud), and serves data to a React frontend.

---

## Features

* Scrapes ShopBack Australia for store cashback offers.
* Stores offers in **SQLite (local)** or **Postgres (cloud)**.
* REST API endpoints:

    * `/offers` — Returns all stored offers as JSON.
    * `/scrape-now` — Triggers a manual background scrape.
* Automatic scraping **every 6 hours** using APScheduler.
* Free Render instances are kept alive by self-pinging `/offers` every 5 minutes.
* React frontend fetches live offers and displays in a table.

---

## Backend Setup

### Requirements

* Python 3.10+
* Node.js / npm (for frontend)
* PostgreSQL (if using cloud database)
* Render or similar hosting for deployment

### Install dependencies

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
playwright install chromium
```

### Environment Variables

Set the database URL:

```bash
export DATABASE_URL="postgresql://<user>:<password>@<host>:<port>/<database>"
```

If not provided, the backend will use a local SQLite file: `offers.db`.

---

## Run Locally

```bash
cd backend
source .venv/bin/activate
python app.py
```

* Visit `http://127.0.0.1:5000/offers` to see the offers.
* Visit `http://127.0.0.1:5000/scrape-now` to trigger a manual scrape.

---

## Frontend Setup (React)

1. Install dependencies:

```bash
cd frontend
npm install
```

2. Update API URL in `frontend/src/api.js`:

```js
export async function fetchOffers() {
  const res = await fetch("https://your-backend.onrender.com/offers");
  if (!res.ok) throw new Error("Failed");
  return res.json();
}
```

3. Run locally:

```bash
npm start
```

---

## Deploy on Render

1️⃣ **Create Web Service**

* Go to Render Dashboard → New → Web Service
* Connect your GitHub repo (`offers-hub`)

2️⃣ **Set Environment Variables**

* `DATABASE_URL="postgresql://<user>:<password>@<host>:<port>/<database>"`

3️⃣ **Configure Build Command**

```bash
pip install --upgrade pip setuptools wheel && pip install -r backend/requirements.txt && playwright install chromium
```

4️⃣ **Configure Start Command**

```bash
gunicorn -w 4 -b 0.0.0.0:$PORT backend.app:app
```

5️⃣ **Deploy**

* Render installs dependencies, Playwright, and starts the backend.

6️⃣ **Scheduler & Keep-alive**

* APScheduler in `app.py` scrapes every 6 hours automatically.
* `/offers` endpoint is self-pinged every 5 minutes to prevent free instance shutdown.

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

```
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

## CSV Import (Optional)

If you have an existing `shopback_offers.csv`:

```bash
python import_csv.py
```

This script will load CSV data into the configured database.

---

## Notes

* Free Render instances can **spin down** with inactivity; self-ping keeps it alive.
* APScheduler ensures **automated scraping** every 6 hours.
* Backend stores data in a database to **prevent memory issues**.

---
Absolutely — I’ve got it. We’ll include that you already have `import_csv_to_db.py` in the workflow, so it’s clear it’s pre-existing and part of the pipeline. Here’s a clear diagram and explanation for your README:

---

### **Offers Hub Data Flow**

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

### **Explanation**

1. **CSV Import (Pre-existing)**

    * Script: `backend/import_csv_to_db.py`
    * Reads `shopback_offers.csv`.
    * Inserts rows into the database (clears previous offers first).

2. **Database**

    * Can be **SQLite** (local) or **Postgres** (cloud, via `DATABASE_URL`).
    * Holds the current set of offers.
    * All updates happen here — scraper overwrites old entries.

3. **Scraper**

    * Endpoint: `/scrape-now`
    * Scheduled every 6 hours via APScheduler in `app.py`.
    * Fetches live ShopBack data, updates DB.

4. **Frontend**

    * Fetches offers from `/offers`.
    * React table columns: `store`, `cashback`, `link`, `scraped_at`.

5. **Idle Keep-Alive (Optional)**

    * Scheduled fetch every 5 minutes to `/offers` keeps Render instance alive.

---
=