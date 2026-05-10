import asyncio
import argparse
import logging
import sys

from src.scraper.api_mode import XApiScraper
from src.scraper.web_mode import XWebScraper
from src.processor.cleaner import TextCleaner
from src.processor.analyzer import SentimentAnalyzer
from src.utils.helpers import ensure_dir, save_to_jsonl
from src.utils.config import DEFAULT_QUERY, DEFAULT_LIMIT

# ────────────
# Logging setup
# ────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ────────
# Pipeline
# ────────

async def run_project(mode: str, query: str, limit: int) -> None:
    """
    Run the sentiment analysis pipeline.
    
    Parameters
    ----------
    mode : str
        Either 'api' (X API) or 'web' (browser scraping). 
        When 'api' is set, web scraping is disabled.
    query : str
        Search keyword or phrase
    limit : int
        Maximum number of tweets to collect
    """
    ensure_dir("data/raw")
    ensure_dir("data/processed")

    output_path = "data/processed/to_label.jsonl"

    # Scraping
    logger.info("Starting %s scraper | query=%r | limit=%d", mode, query, limit)

    raw_data: list[dict] = []

    if mode == "api":
        try:
            scraper = XApiScraper()
            raw_data = scraper.scrape_with_api(query, limit)
        except RuntimeError as exc:
            logger.error("API scraper failed to initialise: %s", exc)
            logger.error("Tip: add X_BEARER_TOKEN to your .env file, then retry.")
            sys.exit(1)
    elif mode == "web":
        scraper_web = XWebScraper()
        raw_data = await scraper_web.scrape_no_api(query, limit)
    else:
        logger.error("Invalid mode: %s. Choose 'api' or 'web'.", mode)
        sys.exit(1)

    if not raw_data:
        logger.warning("No tweets collected. Nothing to process.")
        return

    # Processing & Analysis
    cleaner = TextCleaner()
    analyzer = SentimentAnalyzer()

    processed_count = 0
    for item in raw_data:
        raw_text = item.get("raw_text", "")
        if not raw_text:
            continue

        # Clean text
        cleaned_text = cleaner.basic_clean(raw_text)
        final_text = cleaner.replace_slang(cleaned_text)

        # Detect slang before cleaning
        slang_found = cleaner.detect_slang(raw_text)

        # Analyse
        analysis = analyzer.analyze(final_text)

        # Build record for labeling
        record = {
            "tweet_id": item.get("tweet_id", ""),
            "text": final_text,
            "raw_text": raw_text,
            "label": "Pending",     # to be filled by your labeling UI
            "confidence_score": 0.0,
            "metadata": {
                "is_sarcasm": analysis["is_sarcasm"],
                "is_firm": analysis["is_firm"],
                "mode_used": mode,
                "slang_detected": slang_found,
                "timestamp": item.get("timestamp", ""),
                "author_id": item.get("author_id", ""),
                "metrics": item.get("metrics", {}),
            },
        }

        save_to_jsonl(record, output_path)
        processed_count += 1

    logger.info("Done! %d records saved to %s", processed_count, output_path)


# ───
# CLI
# ───

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scrape and process Indonesian tweets for sentiment labeling."
    )
    parser.add_argument(
        "--mode",
        choices=["api", "web"],
        default="web",
        help="'api' uses the X API (needs X_BEARER_TOKEN), 'web' uses browser scraping (mutually exclusive).",
    )
    parser.add_argument(
        "--query",
        default=DEFAULT_QUERY,
        help="Search keyword or phrase (default: '%(default)s')",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_LIMIT,
        help="Maximum number of tweets to collect (default: %(default)s)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(run_project(args.mode, args.query, args.limit))
