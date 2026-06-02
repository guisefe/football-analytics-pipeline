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


def fetch_standings(season: str) -> list[dict]:
    """Fetch Premier League total standings for the given season start year."""
    url = f"{FOOTBALL_DATA_BASE_URL}/competitions/PL/standings"
    try:
        response = requests.get(
            url,
            headers=FOOTBALL_DATA_HEADERS,
            params={"season": season},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
    except requests.exceptions.Timeout:
        raise RuntimeError(f"Request timed out fetching standings for season {season}")
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"HTTP {response.status_code} fetching standings: {e}")

    standings = response.json().get("standings", [])
    total = next((s for s in standings if s.get("type") == "TOTAL"), standings[0])
    table = total.get("table", [])
    logger.info("Fetched standings for %d teams — season %s", len(table), season)
    return table


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    table = fetch_standings(FOOTBALL_DATA_SEASON)
    load_to_bronze(table, "standings")
