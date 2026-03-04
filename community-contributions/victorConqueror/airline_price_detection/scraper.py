import re
import asyncio
import traceback
from playwright.async_api import async_playwright

async def scrape_travelwings_prices(origin: str, destination: str, date: str, cabin_class: str = "Economy", adults: int = 1) -> str:
    """
    Scrapes the Travelwings site for an exact flight route. 
    Returns the extracted text focusing on common currency symbols (NGN, $, etc).
    """
    
    # Build the specialized URL
    url = f"https://www.travelwings.com/ng/en/flight-search/oneway/{origin}-{destination}/{date}/{cabin_class}/{adults}Adult"
    
    print(f"[STEP 1] Built URL: {url}")
    
    try:
        print("[STEP 2] Starting async_playwright()...")
        async with async_playwright() as p:
            print("[STEP 3] Playwright started! Launching Chromium browser (headless)...")
            browser = await p.chromium.launch(headless=True)
            print("[STEP 4] Browser launched! Creating new page...")
            page = await browser.new_page()
            print("[STEP 5] Page created! Navigating to URL...")
            
            await page.goto(url, wait_until="networkidle", timeout=60000)
            print("[STEP 6] Page loaded (networkidle)! Waiting 5 extra seconds for JS rendering...")
            
            await page.wait_for_timeout(5000)
            print("[STEP 7] Wait complete! Extracting page text...")
            
            text = await page.evaluate("() => document.body.innerText")
            print(f"[STEP 8] Got {len(text)} characters of text from page!")
            
            # Print first 500 chars so we can see what we got
            print(f"[DEBUG] First 500 chars of scraped text:\n{text[:500]}")
            
            await browser.close()
            print("[STEP 9] Browser closed! Now filtering for prices...")
            
            # Split lines and filter out empty ones
            lines = [line.strip() for line in text.split("\n") if line.strip()]
            print(f"[STEP 10] Split into {len(lines)} non-empty lines")
            
            currency_symbols = ["$", "\u20ac", "\u00a3", "\u20a6", "USD", "EUR", "GBP", "NGN"]
            relevant_lines = []
            
            for i, line in enumerate(lines):
                if any(sym in line for sym in currency_symbols) or "Air Peace" in line or "Airline" in line or "Economy" in line or "Business" in line:
                    start_idx = max(0, i - 3)
                    end_idx = min(len(lines), i + 4)
                    context_chunk = " | ".join(lines[start_idx:end_idx])
                    
                    if context_chunk not in relevant_lines:
                        relevant_lines.append(context_chunk)
            
            print(f"[STEP 11] Found {len(relevant_lines)} relevant price chunks")
            
            if not relevant_lines:
                print("[STEP 12] No price lines found! Returning raw text as fallback...")
                return f"Raw scraped text from Travelwings:\n{text[:10000]}"
            
            result = f"Here is the scraped pricing information from {url}:\n\n" + "\n".join(relevant_lines)
            print(f"[STEP 12] SUCCESS! Returning {len(result)} chars of results")
            return result
            
    except Exception as e:
        error_msg = f"An error occurred while fetching Travelwings: {str(e)}"
        print(f"[ERROR] {error_msg}")
        print(f"[TRACEBACK]\n{traceback.format_exc()}")
        return error_msg

if __name__ == "__main__":
    print("Testing Travelwings Scraper...")
    sample_result = asyncio.run(scrape_travelwings_prices("ABV", "LOS", "2026-03-03", "Economy", 1))
    print("\n=== FINAL RESULT ===")
    print(sample_result)
