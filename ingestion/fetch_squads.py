import logging
import time

import duckdb
import requests

from ingestion.config import (
    FOOTBALL_DATA_BASE_URL,
    FOOTBALL_DATA_HEADERS,
    FOOTBALL_DATA_RATE_LIMIT_SLEEP,
    DUCKDB_PATH,
    REQUEST_TIMEOUT,
    FOOTBALL_DATA_SEASON,
)
from ingestion.db import load_to_bronze

logger = logging.getLogger(__name__)


def get_team_ids() -> list[int]:
    """Read Premier League team IDs from Bronze standings table."""
    with duckdb.connect(DUCKDB_PATH) as conn:
        rows = conn.execute("SELECT team.id FROM bronze.standings").fetchall()
    ids = [row[0] for row in rows]
    logger.info("Loaded %d team IDs from bronze.standings", len(ids))
    return ids


def fetch_squad(team_id: int) -> dict | None:
    """Fetch squad for a single team. Returns None on HTTP error."""
    try:
        response = requests.get(
            f"{FOOTBALL_DATA_BASE_URL}/teams/{team_id}",
            headers=FOOTBALL_DATA_HEADERS,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        logger.warning("Failed to fetch squad for team %d: %s", team_id, e)
        return None


def fetch_all_squads(team_ids: list[int]) -> list[dict]:
    """Fetch squads for all teams respecting the 10 req/min rate limit."""
    squads = []
    for i, team_id in enumerate(team_ids):
        logger.info("Fetching squad %d/%d — team_id: %d", i + 1, len(team_ids), team_id)
        squad = fetch_squad(team_id)
        if squad:
            squads.append(squad)
        time.sleep(FOOTBALL_DATA_RATE_LIMIT_SLEEP)
    return squads


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    team_ids = get_team_ids()
    squads = fetch_all_squads(team_ids)
    load_to_bronze(squads, "squads")
