import logging
from pathlib import Path
from typing import Any

import duckdb

from ingestion.config import DUCKDB_PATH

logger = logging.getLogger(__name__)


def get_connection() -> duckdb.DuckDBPyConnection:
    """Return a DuckDB connection to the warehouse file."""
    Path(DUCKDB_PATH).parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(DUCKDB_PATH)


def load_to_bronze(records: list[dict[str, Any]], table: str) -> None:
    """
    Insert raw API records into a Bronze table.
    Creates the table on first run. Skips duplicates on subsequent runs.
    """
    if not records:
        logger.warning("No records to load into bronze.%s", table)
        return

    with get_connection() as conn:
        conn.execute("CREATE SCHEMA IF NOT EXISTS bronze")
        conn.execute(f"""
            CREATE TABLE IF NOT EXISTS bronze.{table} AS
            SELECT * FROM records WHERE 1=0
        """)
        existing = conn.execute(f"SELECT COUNT(*) FROM bronze.{table}").fetchone()[0]
        conn.executemany(
            f"INSERT OR IGNORE INTO bronze.{table} SELECT * FROM ?",
            [[r] for r in records]
        )
        new_count = conn.execute(f"SELECT COUNT(*) FROM bronze.{table}").fetchone()[0]
        inserted = new_count - existing
        logger.info("bronze.%s — inserted %d new records (total: %d)", table, inserted, new_count)
