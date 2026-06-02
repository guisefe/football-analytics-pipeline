import os
from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator
from cosmos import DbtTaskGroup, ProjectConfig, ProfileConfig, ExecutionConfig
from cosmos.profiles import DuckDBUserPasswordProfileMapping

DBT_PROJECT_DIR = Path(os.environ["DBT_PROJECT_DIR"])
DUCKDB_PATH = os.environ["DUCKDB_PATH"]

default_args = {
    "owner": "guisefe",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
}


def run_ingestion(module: str) -> None:
    """Import and execute a named ingestion module."""
    import importlib
    mod = importlib.import_module(f"ingestion.{module}")
    mod.main()


with DAG(
    dag_id="pl_pipeline",
    description="Premier League end-to-end pipeline — Bronze → Silver → Gold",
    schedule="0 6 * * *",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    default_args=default_args,
    tags=["football", "dbt", "duckdb"],
) as dag:

    fetch_matches = PythonOperator(
        task_id="fetch_matches",
        python_callable=run_ingestion,
        op_args=["fetch_matches"],
        pool="duckdb_pool",
    )

    fetch_scorers = PythonOperator(
        task_id="fetch_scorers",
        python_callable=run_ingestion,
        op_args=["fetch_scorers"],
        pool="duckdb_pool",
    )

    fetch_standings = PythonOperator(
        task_id="fetch_standings",
        python_callable=run_ingestion,
        op_args=["fetch_standings"],
        pool="duckdb_pool",
    )

    fetch_squads = PythonOperator(
        task_id="fetch_squads",
        python_callable=run_ingestion,
        op_args=["fetch_squads"],
        pool="duckdb_pool",
    )

    fetch_player_stats = PythonOperator(
        task_id="fetch_player_stats",
        python_callable=run_ingestion,
        op_args=["fetch_player_stats"],
        pool="duckdb_pool",
    )

    dbt_transformations = DbtTaskGroup(
        group_id="dbt_transformations",
        project_config=ProjectConfig(DBT_PROJECT_DIR),
        profile_config=ProfileConfig(
            profile_name="football_analytics",
            target_name="dev",
            profile_mapping=DuckDBUserPasswordProfileMapping(
                conn_id="duckdb_default",
                profile_args={"path": DUCKDB_PATH},
            ),
        ),
        execution_config=ExecutionConfig(
            dbt_executable_path="dbt",
        ),
        operator_args={"pool": "duckdb_pool"},
    )

    [fetch_matches, fetch_scorers, fetch_standings, fetch_squads, fetch_player_stats] >> dbt_transformations
