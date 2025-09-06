import asyncio
import csv
from playwright.async_api import async_playwright

CSV_FILE = "shopback_offers.csv"
DESIRED_CATEGORIES = ["Fashion", "Electronics", "Food", "Marketplace", "Home & Ga"]
MAX_RETRIES = 2

async def scrape_merchant(browser, name, link, category):
    for attempt in range(1, MAX_RETRIES + 1):
        detail_page = await browser.new_page()
        try:
            await detail_page.goto(link, timeout=15000)
            await detail_page.wait_for_timeout(3000)

            new_cb_el = await detail_page.query_selector("div:has-text('New users') span")
            existing_cb_el = await detail_page.query_selector("div:has-text('Existing users') span")

            new_cb = await new_cb_el.inner_text() if new_cb_el else "N/A"
            existing_cb = await existing_cb_el.inner_text() if existing_cb_el else "N/A"

            await detail_page.close()
            return new_cb.strip(), existing_cb.strip()
        except Exception as e:
            print(f"⚠️ Attempt {attempt} failed for {link}: {e}")
            await detail_page.close()
            if attempt == MAX_RETRIES:
                return "N/A", "N/A"

async def run_scraper():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, slow_mo=200)
        page = await browser.new_page()
        await page.goto("https://www.shopback.com.au/all-stores", timeout=60000)

        for _ in range(10):
            await page.mouse.wheel(0, 3000)
            await page.wait_for_timeout(2000)

        cards = await page.query_selector_all("div.cursor_pointer.pos_relative")
        scraped = []

        for card in cards:
            name = await card.get_attribute("data-merchant-name")
            link = await card.get_attribute("data-feature-destination-url")
            category = await card.get_attribute("data-l1-category-name")

            if not link or (DESIRED_CATEGORIES and category not in DESIRED_CATEGORIES):
                continue

            new_cb, existing_cb = await scrape_merchant(browser, name, link, category)
            scraped.append([
                name.strip() if name else "N/A",
                new_cb,
                existing_cb,
                link.strip(),
                category.strip() if category else "N/A"
            ])

        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Store", "New User Cashback", "Existing User Cashback", "Link", "Category"])
            writer.writerows(scraped)

        print(f"✅ Scraped {len(scraped)} offers into {CSV_FILE}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_scraper())
