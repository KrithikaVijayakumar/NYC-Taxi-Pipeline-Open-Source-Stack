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
        import pyarrow.parquet as pq
        import pyarrow as pa
        import boto3
        from botocore.client import Config
        import io

        s3 = boto3.client(
            "s3",
            endpoint_url="http://minio:9000",
            aws_access_key_id="admin",
            aws_secret_access_key="password",
            config=Config(signature_version="s3v4"),
        )

        # Read from bronze
        obj = s3.get_object(Bucket="bronze", Key="taxi/green/year=2023/month=01/data.parquet")
        table = pq.read_table(io.BytesIO(obj["Body"].read()))

        # Convert to pandas for transformations
        df = table.to_pandas()

        # Clean data
        df = df[df["trip_distance"] > 0]
        df = df[df["fare_amount"] > 0]
        df = df[df["total_amount"] > 0]
        df = df.drop_duplicates()

        # Add derived columns
        df["trip_duration_min"] = (
            df["lpep_dropoff_datetime"] - df["lpep_pickup_datetime"]
        ).dt.total_seconds() / 60
        df["year"] = df["lpep_pickup_datetime"].dt.year
        df["month"] = df["lpep_pickup_datetime"].dt.month
        df["ingested_at"] = pa.array([None] * len(df))

        # Filter outliers
        df = df[df["trip_duration_min"].between(1, 180)]

        # Write to silver
        buffer = io.BytesIO()
        df.to_parquet(buffer, index=False)
        buffer.seek(0)
        s3.put_object(
            Bucket="silver",
            Key="taxi/green/year=2023/month=01/data.parquet",
            Body=buffer.getvalue()
        )

        # Also save locally for dbt
        df.to_parquet("/tmp/silver.parquet", index=False)
        print(f"✅ Silver complete: {len(df):,} rows")
    @task()
    def run_dbt():
        import subprocess
        subprocess.run(
            ["/home/airflow/.local/bin/dbt", "run",
             "--project-dir", "/opt/airflow/transformations/dbt",
             "--profiles-dir", "/opt/airflow/transformations/dbt"],
            check=True
        )

    ingest_bronze() >> transform_silver() >> run_dbt()

nyc_taxi_pipeline()