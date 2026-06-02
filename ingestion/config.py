import os
from pathlib import Path

# APIs
FOOTBALL_DATA_BASE_URL = "https://api.football-data.org/v4"
API_FOOTBALL_BASE_URL = "https://v3.football.api-sports.io"
COMPETITION_CODE = "PL"
FOOTBALL_DATA_SEASON = "2025"
API_FOOTBALL_LEAGUE_ID = 39
API_FOOTBALL_SEASON = 2024

# Auth
FOOTBALL_DATA_API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY")

FOOTBALL_DATA_HEADERS = {"X-Auth-Token": FOOTBALL_DATA_API_KEY}
API_FOOTBALL_HEADERS = {"x-apisports-key": API_FOOTBALL_KEY}

# Storage
DUCKDB_PATH = os.getenv("DUCKDB_PATH", str(Path(__file__).parent.parent / "data" / "warehouse.duckdb"))

# Rate limits
FOOTBALL_DATA_RATE_LIMIT_SLEEP = 6  # 10 req/min — 6s between requests
REQUEST_TIMEOUT = 30
