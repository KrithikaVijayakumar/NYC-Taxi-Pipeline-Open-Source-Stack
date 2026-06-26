#  NYC Taxi Data Pipeline

End-to-end batch data pipeline processing NYC TLC taxi data using 100% open source tools.

## Architecture


## Tech Stack
| Layer | Tool |
|---|---|
| Storage | MinIO (S3-compatible) |
| Ingestion | Python, requests, pyarrow |
| Transformation | PySpark, dbt Core |
| Orchestration | Apache Airflow |
| Query Engine | DuckDB |
| Containers | Docker Compose |

## How to Run

### 1. Start the stack
```bash
docker compose up -d
```

### 2. Run ingestion
```bash
python -m ingestion.taxi_client
```

### 3. Trigger the pipeline
Open Airflow at http://localhost:8081 and trigger `nyc_taxi_pipeline`

## Design Decisions
- **MinIO over AWS S3** — fully local, no cloud costs, S3-compatible API
- **PySpark over Pandas** — handles large files (4GB+/month) without memory issues
- **Partitioned by year/month** — dramatically speeds up time-range queries
- **dbt for gold layer** — version controlled SQL with built-in testing