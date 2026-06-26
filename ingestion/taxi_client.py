import requests
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"

TAXI_TYPES = {
    "yellow": "yellow_tripdata",
    "green": "green_tripdata",
}

class TaxiClient:
    def __init__(self, download_dir: str = "/tmp/taxi"):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)

    def build_url(self, taxi_type: str, year: int, month: int) -> str:
        prefix = TAXI_TYPES[taxi_type]
        return f"{BASE_URL}/{prefix}_{year}-{month:02d}.parquet"

    def download(self, taxi_type: str, year: int, month: int) -> Path:
        url = self.build_url(taxi_type, year, month)
        dest = self.download_dir / f"{taxi_type}_{year}_{month:02d}.parquet"

        if dest.exists():
            logger.info(f"Already downloaded: {dest}")
            return dest

        logger.info(f"Downloading {url}")
        resp = requests.get(url, stream=True, timeout=60)
        resp.raise_for_status()

        with open(dest, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)

        logger.info(f"Saved to {dest}")
        return dest