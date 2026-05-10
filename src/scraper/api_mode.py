import logging
from typing import Optional
import tweepy
from src.utils.config import (
    BEARER_TOKEN,
    CONSUMER_KEY,
    CONSUMER_SECRET,
    ACCESS_TOKEN,
    ACCESS_SECRET,
    MAX_RESULTS_PER_PAGE,
)

logger = logging.getLogger(__name__)


def _build_client() -> Optional[tweepy.Client]:
    """
    Build a Tweepy v2 Client using the best available credentials.

    Priority:
      1. Bearer Token only  → app-only OAuth 2.0 (read public tweets, fastest)
      2. All OAuth 1.0a keys → user-context (needed for write operations)
      3. Both at once       → tweepy accepts this and uses the right one per call
    """
    has_bearer = bool(BEARER_TOKEN)
    has_oauth1 = all([CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET])

    if not has_bearer and not has_oauth1:
        logger.error(
            "No API credentials found. "
            "Add X_BEARER_TOKEN (and optionally X_CONSUMER_KEY / X_CONSUMER_SECRET / "
            "X_ACCESS_TOKEN / X_ACCESS_SECRET) to your .env file."
        )
        return None

    if has_bearer and has_oauth1:
        logger.info("Using Bearer Token + OAuth 1.0a (full access)")
        return tweepy.Client(
            bearer_token=BEARER_TOKEN,
            consumer_key=CONSUMER_KEY,
            consumer_secret=CONSUMER_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_SECRET,
            wait_on_rate_limit=True,
        )

    if has_bearer:
        logger.info("Using Bearer Token (OAuth 2.0 app-only — read-only search)")
        return tweepy.Client(bearer_token=BEARER_TOKEN, wait_on_rate_limit=True)

    # OAuth 1.0a only (rare but valid)
    logger.info("Using OAuth 1.0a user-context credentials")
    return tweepy.Client(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_SECRET,
        wait_on_rate_limit=True,
    )


class XApiScraper:
    """
    Scrape tweets using the official X (Twitter) API v2.

    By default, searching recent tweets only requires a BEARER_TOKEN.
    No OAuth 1.0a keys are needed for public search.
    """

    def __init__(self):
        self.client = _build_client()
        if self.client is None:
            raise RuntimeError(
                "Could not initialise X API client. Check your .env credentials."
            )

    def scrape_with_api(self, query: str, limit: int = 10) -> list[dict]:
        """
        Search recent tweets (last 7 days on free/basic tier) and return
        a list of dicts with tweet_id, raw_text, and timestamp.

        Parameters
        ----------
        query : str
            Search keyword or phrase, e.g. "layanan bank kecewa"
        limit : int
            Maximum number of tweets to collect (capped at 100 per API call on
            free tier; raises multiple paginated calls automatically for more).
        """
        tweets_data: list[dict] = []

        # Build a clean query: exclude retweets, filter to Indonesian
        full_query = f"{query} -is:retweet lang:id"

        try:
            # Paginate automatically when limit > MAX_RESULTS_PER_PAGE
            for response in tweepy.Paginator(
                self.client.search_recent_tweets,
                query=full_query,
                max_results=min(limit, MAX_RESULTS_PER_PAGE),
                tweet_fields=["created_at", "author_id", "public_metrics", "text"],
                limit=1,  # number of *pages* — we fetch one page, then stop manually
            ):
                if response.data is None:
                    logger.warning("API returned no data for query: %s", query)
                    break

                for tweet in response.data:
                    tweets_data.append({
                        "tweet_id": str(tweet.id),
                        "raw_text": tweet.text,
                        "timestamp": str(tweet.created_at) if tweet.created_at else "",
                        "author_id": str(tweet.author_id) if tweet.author_id else "",
                        "metrics": tweet.public_metrics or {},
                    })

                    if len(tweets_data) >= limit:
                        break

                if len(tweets_data) >= limit:
                    break

        except tweepy.errors.Unauthorized:
            logger.error(
                "Unauthorized (401). Your Bearer Token or OAuth keys are invalid or expired. "
                "Double-check X_BEARER_TOKEN in your .env file."
            )
        except tweepy.errors.Forbidden:
            logger.error(
                "Forbidden (403). Your app may not have permission to search tweets. "
                "Make sure your X Developer App has 'Read' permissions enabled."
            )
        except tweepy.errors.TooManyRequests:
            logger.error(
                "Rate limit hit (429). Tweepy should handle this automatically with "
                "wait_on_rate_limit=True, but the free tier has strict monthly caps."
            )
        except tweepy.errors.TweepyException as exc:
            logger.error("Tweepy error: %s", exc)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Unexpected error during API scrape: %s", exc)

        logger.info("API scrape complete: %d tweets collected", len(tweets_data))
        return tweets_data
