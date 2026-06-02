.PHONY: init up down restart logs ingest dbt-run dbt-test dbt-debug lint test clean help

help:
	@echo "Available commands:"
	@echo "  make init       — Initialize Airflow (first time only)"
	@echo "  make up         — Start all services"
	@echo "  make down       — Stop all services"
	@echo "  make restart    — Restart all services"
	@echo "  make logs       — View Airflow logs"
	@echo "  make ingest     — Run ingestion scripts manually"
	@echo "  make dbt-run    — Run dbt models"
	@echo "  make dbt-test   — Run dbt tests"
	@echo "  make dbt-debug  — Debug dbt connection"
	@echo "  make lint       — Lint SQL models with sqlfluff"
	@echo "  make test       — Run Python tests"
	@echo "  make clean      — Remove all containers and volumes"

init:
	docker compose up airflow-init

up:
	docker compose up -d airflow-webserver airflow-scheduler postgres
	@echo "Airflow UI: http://localhost:8080 (admin/admin)"

down:
	docker compose down

restart:
	docker compose restart airflow-webserver airflow-scheduler

logs:
	docker compose logs -f airflow-scheduler

ingest:
	docker compose exec airflow-scheduler python /opt/airflow/ingestion/fetch_matches.py
	docker compose exec airflow-scheduler python /opt/airflow/ingestion/fetch_scorers.py
	docker compose exec airflow-scheduler python /opt/airflow/ingestion/fetch_standings.py
	docker compose exec airflow-scheduler python /opt/airflow/ingestion/fetch_squads.py
	docker compose exec airflow-scheduler python /opt/airflow/ingestion/fetch_player_stats.py

dbt-run:
	docker compose exec airflow-scheduler bash -c "cd /opt/airflow/dbt && dbt run"

dbt-test:
	docker compose exec airflow-scheduler bash -c "cd /opt/airflow/dbt && dbt test"

dbt-debug:
	docker compose exec airflow-scheduler bash -c "cd /opt/airflow/dbt && dbt debug"

lint:
	sqlfluff lint dbt/models --dialect duckdb

test:
	pytest ingestion/tests/ -v --cov=ingestion --cov-report=term-missing

clean:
	docker compose down -v --remove-orphans
	rm -f data/warehouse.duckdb
