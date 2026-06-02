FROM apache/airflow:2.9.0-python3.11

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir \
    astronomer-cosmos==1.7.0 \
    dbt-core==1.8.0 \
    dbt-duckdb==1.8.4 \
    duckdb==1.0.0 \
    requests==2.31.0 \
    python-dotenv==1.0.1
