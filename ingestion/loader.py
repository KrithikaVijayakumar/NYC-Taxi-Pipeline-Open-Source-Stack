import boto3
from botocore.client import Config
from pathlib import Path

def get_minio_client():
    return boto3.client(
        "s3",
        endpoint_url="http://minio:9000",
        aws_access_key_id="admin",
        aws_secret_access_key="password",
        config=Config(signature_version="s3v4"),
    )

def load_to_bronze(file_path: Path, taxi_type: str, year: int, month: int):
    s3 = get_minio_client()
    key = f"taxi/{taxi_type}/year={year}/month={month:02d}/data.parquet"

    s3.upload_file(
        Filename=str(file_path),
        Bucket="bronze",
        Key=key,
    )
    print(f"Uploaded {file_path.name} → bronze/{key}")