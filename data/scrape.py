from urllib.parse import urlparse
from playwright.async_api import async_playwright


def _detect_retailer(url: str) -> str:
    host = urlparse(url).hostname or ""
    if "target.com" in host:
        return "target"
    raise ValueError(f"Unsupported retailer URL: {url}")


async def _scrape_target(page, product_url: str) -> dict:
    await page.goto(product_url, wait_until="domcontentloaded", timeout=30000)
    await page.evaluate("""
        async () => {
            for (let i = 0; i < 10; i++) {
                window.scrollBy(0, 800);
                await new Promise(r => setTimeout(r, 400));
            }
            document.querySelectorAll('button, summary, [role="button"]').forEach(el => {
                const text = (el.innerText || el.textContent || "").toLowerCase().trim();
                if (text.includes('specification') || text.includes('details') || text.includes('show more')) {
                    try { el.click(); } catch(e) {}
                }
            });
        }
    """)
    try:
        await page.wait_for_selector('[data-test="item-details-specifications"]', timeout=15000)
    except Exception:
        print(f"  Warning: specs selector not found, using available page text")
    product_image_url = await page.locator('meta[property="og:image"]').first.get_attribute("content")
    text = await page.evaluate("document.body.innerText")
    product_description = "\n".join([line.strip() for line in text.splitlines() if line.strip()])
    return {
        "product_url": product_url,
        "product_image_url": product_image_url,
        "product_description": product_description[:6000],
    }


async def scrape_product_page(product_url: str) -> dict:
    retailer = _detect_retailer(product_url)
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        try:
            if retailer == "target":
                result = await _scrape_target(page, product_url)
        finally:
            await browser.close()
    return result
