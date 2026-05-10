import asyncio
import hashlib
import logging
from typing import Optional

from playwright.async_api import async_playwright, Page
from playwright_stealth.async_api import stealth
from src.utils.config import TWEET_SELECTOR, TEXT_SELECTOR

logger = logging.getLogger(__name__)

PAGE_LOAD_WAIT_MS = 7_000
SCROLL_DELAY_SEC = 2.5
SCROLL_STEP_PX = 1_200

def _stable_id(text: str) -> str:
    """Generate a stable, short ID for a tweet based on its content."""
    return "web_" + hashlib.sha1(text.encode()).hexdigest()[:12]

async def _scroll_and_collect(
    page: Page,
    limit: int,
    max_scroll_attempts: int = 30,
) -> list[dict]:
    """
    Scroll the page, collecting tweet data until `limit` is reached
    or `max_scroll_attempts` consecutive scrolls yield no new content.
    """
    results: list[dict] = []
    seen_texts: set[str] = set()
    stale_scrolls = 0

    while len(results) < limit and stale_scrolls < max_scroll_attempts:
        tweets = await page.query_selector_all(TWEET_SELECTOR)
        new_this_round = 0

        for tweet in tweets:
            if len(results) >= limit:
                break
            try:
                text_elem = await tweet.query_selector(TEXT_SELECTOR)
                if text_elem is None:
                    continue
                content = (await text_elem.inner_text()).strip()
                if not content or content in seen_texts:
                    continue

                seen_texts.add(content)
                results.append({
                    "tweet_id": _stable_id(content),
                    "raw_text": content,
                    "timestamp": "",  # not available via web scraping
                })
                new_this_round += 1
            except Exception:  # noqa: BLE001
                continue

        if new_this_round == 0:
            stale_scrolls += 1
        else:
            stale_scrolls = 0

        if len(results) < limit:
            await page.evaluate(f"window.scrollBy(0, {SCROLL_STEP_PX})")
            await asyncio.sleep(SCROLL_DELAY_SEC)

    return results

class XWebScraper:
    """
    Scrape tweets from X.com using Playwright browser automation.
    
    Uses playwright-stealth to bypass anti-bot detection.
    """

    USER_AGENT = (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )

    async def scrape_no_api(self, query: str, limit: int = 10) -> list[dict]:
        """
        Scrape tweets from X.com using browser automation (no API required).
        
        Parameters
        ----------
        query : str
            Search keyword or phrase
        limit : int
            Maximum number of tweets to collect
            
        Returns
        -------
        list[dict]
            List of tweet records with tweet_id, raw_text, and timestamp
        """
        results: list[dict] = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=self.USER_AGENT,
                locale="id-ID",
                timezone_id="Asia/Jakarta",
            )
            page = await context.new_page()
            await stealth(page)

            url = f"https://x.com/search?q={query}&src=typed_query&f=live"
            logger.info("Navigating to: %s", url)

            try:
                await page.goto(url, timeout=30_000)
                logger.info("Waiting %d ms for page render...", PAGE_LOAD_WAIT_MS)
                await page.wait_for_timeout(PAGE_LOAD_WAIT_MS)

                results = await _scroll_and_collect(page, limit)

            except Exception as exc:  # noqa: BLE001
                logger.error("Web scrape error: %s", exc)
            finally:
                await browser.close()

        logger.info("Web scrape complete: %d tweets collected", len(results))
        return results[:limit]
