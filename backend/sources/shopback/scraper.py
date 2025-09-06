import asyncio
import csv
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        # Set headless=False so you can see the browser in action
        browser = await p.chromium.launch(headless=False, slow_mo=200)
        page = await browser.new_page()

        # ShopBack all stores URL – you can swap this with any category/URL
        await page.goto("https://www.shopback.com.au/all-stores", timeout=60000)

        # Scroll to load more offers
        for _ in range(8):  # adjust to scroll deeper
            await page.mouse.wheel(0, 3000)
            await page.wait_for_timeout(2000)

        # Grab merchant cards via data attributes
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

        # Save to CSV
        with open("shopback_offers.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Store", "Cashback (%)", "Link"])
            writer.writerows(scraped)

        print(f"✅ Scraped {len(scraped)} offers into shopback_offers.csv")
        await browser.close()

asyncio.run(run())
