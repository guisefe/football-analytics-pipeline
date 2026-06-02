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


def fetch_matches(season: str) -> list[dict]:
    """Fetch all Premier League matches for the given season start year."""
    url = f"{FOOTBALL_DATA_BASE_URL}/competitions/PL/matches"
    try:
        response = requests.get(
            url,
            headers=FOOTBALL_DATA_HEADERS,
            params={"season": season},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
    except requests.exceptions.Timeout:
        raise RuntimeError(f"Request timed out fetching matches for season {season}")
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"HTTP {response.status_code} fetching matches: {e}")

    matches = response.json().get("matches", [])
    logger.info("Fetched %d matches for season %s", len(matches), season)
    return matches


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    matches = fetch_matches(FOOTBALL_DATA_SEASON)
    load_to_bronze(matches, "matches")
