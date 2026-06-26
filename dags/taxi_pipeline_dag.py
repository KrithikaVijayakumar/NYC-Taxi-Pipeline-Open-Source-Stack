import sys
sys.path.insert(0, '/opt/airflow')

from airflow.decorators import dag, task
from datetime import datetime

@dag(
    schedule_interval="0 6 1 * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["taxi", "nyc", "batch"],
)
def nyc_taxi_pipeline():

    @task()
    def ingest_bronze():
        from ingestion.taxi_client import TaxiClient
        from ingestion.loader import load_to_bronze

        year = 2023
        month = 1

        client = TaxiClient()
        path = client.download("green", year, month)
        load_to_bronze(path, "green", year, month)

    @task()
    def transform_silver():
        import subprocess
        subprocess.run([
            "docker", "exec", "nyc-taxi-pipeline-spark-1",
            "/opt/spark/bin/spark-submit",
            "--master", "spark://spark:7077",
            "/opt/spark/transformations/spark_jobs/bronze_to_silver.py"
        ], check=True)

    @task()
    def run_dbt():
        import subprocess
        subprocess.run(
            ["dbt", "run", "--project-dir", "transformations/dbt"],
            check=True
        )

    ingest_bronze() >> transform_silver() >> run_dbt()

nyc_taxi_pipeline()