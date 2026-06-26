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
    def ingest_bronze(**context):
        from ingestion.taxi_client import TaxiClient
        from ingestion.loader import load_to_bronze

        year = context["data_interval_start"].year
        month = context["data_interval_start"].month

        client = TaxiClient()
        path = client.download("yellow", year, month)
        load_to_bronze(path, "yellow", year, month)

    @task()
    def transform_silver():
        import subprocess
        subprocess.run([
            "spark-submit",
            "--master", "spark://spark:7077",
            "transformations/spark_jobs/bronze_to_silver.py"
        ], check=True)

    @task()
    def run_dbt():
        import subprocess
        subprocess.run(
            ["dbt", "run", "--project-dir", "transformations/dbt"],
            check=True
        )

    ingest_bronze() >> transform_silver() >> run_dbt()

dag = nyc_taxi_pipeline()