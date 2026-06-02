import logging

import requests

from ingestion.config import (
    FOOTBALL_DATA_BASE_URL,
    FOOTBALL_DATA_HEADERS,
    FOOTBALL_DATA_SEASON,
    REQUEST_TIMEOUT,
)
from ingestion.db import load_to_bronze

logger = logging.getLogger(__name__)


def fetch_scorers(season: str, limit: int = 50) -> list[dict]:
    """Fetch top Premier League scorers for the given season start year."""
    url = f"{FOOTBALL_DATA_BASE_URL}/competitions/PL/scorers"
    try:
        response = requests.get(
            url,
            headers=FOOTBALL_DATA_HEADERS,
            params={"season": season, "limit": limit},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
    except requests.exceptions.Timeout:
        raise RuntimeError(f"Request timed out fetching scorers for season {season}")
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"HTTP {response.status_code} fetching scorers: {e}")

    scorers = response.json().get("scorers", [])
    logger.info("Fetched %d scorers for season %s", len(scorers), season)
    return scorers


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    scorers = fetch_scorers(FOOTBALL_DATA_SEASON)
    load_to_bronze(scorers, "scorers")
