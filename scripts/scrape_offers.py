import os
import json
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

# --- Paths ---
FRONTEND_JSON_PATH = os.path.join(
    os.path.dirname(__file__), "../frontend/src/offers.json"
)

# --- Cashback Normalizer ---
def normalize_cashback(cashback_raw: str) -> str:
    if not cashback_raw:
        return "N/A"
    cb = cashback_raw.strip()
    if "%" in cb:
        try:
            val = float(cb.replace("%", "").strip())
            return f"{val}%" if val <= 100 else f"${int(val)}"
        except:
            return cb
    if "$" in cb:
        return cb
    try:
        val = float(cb)
        return f"{val:g}%" if val <= 100 else f"${int(val)}"
    except ValueError:
        return cb

# --- Scraper ---
async def scrape_shopback():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=[
            "--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"
        ])
        page = await browser.new_page()
        await page.goto("https://www.shopback.com.au/all-stores", timeout=300000)

        # Scroll to load all offers
        prev_count = 0
        stable_scrolls = 0
        max_scroll_attempts = 20
        scroll_count = 0
        while scroll_count < max_scroll_attempts:
            await page.mouse.wheel(0, 1000)
            await asyncio.sleep(2)
            cards = await page.query_selector_all("div.cursor_pointer.pos_relative")
            if len(cards) == prev_count:
                stable_scrolls += 1
            else:
                stable_scrolls = 0
            if stable_scrolls >= 3:
                break
            prev_count = len(cards)
            scroll_count += 1

        # Extract offers
        offers_list = []
        cards = await page.query_selector_all("div.cursor_pointer.pos_relative")
        for card in cards:
            name = await card.get_attribute("data-merchant-name")
            cashback_raw = await card.get_attribute("data-max-cashback-rate")
            link = await card.get_attribute("data-feature-destination-url")
            if name:
                offers_list.append({
                    "id": len(offers_list) + 1,
                    "store": name.strip(),
                    "cashback": normalize_cashback(cashback_raw),
                    "link": link.strip() if link else "N/A",
                    "scraped_at": datetime.now().isoformat()
                })

        await browser.close()
        print(f"✅ Total offers scraped: {len(offers_list)}")
        return offers_list

# --- Main ---
def main():
    offers = asyncio.run(scrape_shopback())

    # Wrap offers with last_updated timestamp
    data_to_save = {
        "last_updated": datetime.now().isoformat(),
        "offers": offers
    }

    os.makedirs(os.path.dirname(FRONTEND_JSON_PATH), exist_ok=True)
    with open(FRONTEND_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data_to_save, f, indent=2)

    print(f"✅ Offers saved to {FRONTEND_JSON_PATH} (total {len(offers)} offers)")


if __name__ == "__main__":
    main()
