import logging

import requests

from ingestion.config import (
    API_FOOTBALL_BASE_URL,
    API_FOOTBALL_HEADERS,
    API_FOOTBALL_LEAGUE_ID,
    API_FOOTBALL_SEASON,
    REQUEST_TIMEOUT,
)
from ingestion.db import load_to_bronze

logger = logging.getLogger(__name__)


def fetch_top_players(endpoint: str) -> list[dict]:
    """Fetch top 20 players from the given ranking endpoint."""
    try:
        response = requests.get(
            f"{API_FOOTBALL_BASE_URL}/{endpoint}",
            headers=API_FOOTBALL_HEADERS,
            params={"league": API_FOOTBALL_LEAGUE_ID, "season": API_FOOTBALL_SEASON},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
    except requests.exceptions.Timeout:
        raise RuntimeError(f"Request timed out: {endpoint}")
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"HTTP {response.status_code} fetching {endpoint}: {e}")

    players = response.json().get("response", [])
    logger.info("%s — fetched %d players", endpoint, len(players))
    return players


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    top_scorers = fetch_top_players("players/topscorers")
    top_assists = fetch_top_players("players/topassists")
    players = list({p["player"]["id"]: p for p in top_scorers + top_assists}.values())
    logger.info("Total unique players: %d", len(players))
    load_to_bronze(players, "player_stats")
