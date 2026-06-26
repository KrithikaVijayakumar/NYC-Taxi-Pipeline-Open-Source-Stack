from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = SparkSession.builder \
    .appName("taxi-bronze-to-silver") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "admin") \
    .config("spark.hadoop.fs.s3a.secret.key", "password") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .getOrCreate()

df = spark.read.parquet("s3a://bronze/taxi/yellow/*/*/data.parquet")

df_clean = (df
    .withColumnRenamed("tpep_pickup_datetime", "pickup_datetime")
    .withColumnRenamed("tpep_dropoff_datetime", "dropoff_datetime")
    .withColumnRenamed("PULocationID", "pickup_location_id")
    .withColumnRenamed("DOLocationID", "dropoff_location_id")
    .filter(F.col("trip_distance") > 0)
    .filter(F.col("fare_amount") > 0)
    .filter(F.col("total_amount") > 0)
    .filter(F.col("passenger_count") > 0)
    .filter(F.col("pickup_datetime") < F.col("dropoff_datetime"))
    .dropDuplicates(["pickup_datetime", "dropoff_datetime",
                     "pickup_location_id", "dropoff_location_id",
                     "total_amount"])
    .withColumn("trip_duration_min",
        (F.unix_timestamp("dropoff_datetime") -
         F.unix_timestamp("pickup_datetime")) / 60)
    .withColumn("speed_mph",
        F.col("trip_distance") / (F.col("trip_duration_min") / 60))
    .withColumn("tip_pct",
        F.round(F.col("tip_amount") / F.col("fare_amount") * 100, 2))
    .withColumn("year", F.year("pickup_datetime"))
    .withColumn("month", F.month("pickup_datetime"))
    .withColumn("ingested_at", F.current_timestamp())
    .filter(F.col("trip_duration_min").between(1, 180))
    .filter(F.col("trip_distance") < 100)
)

df_clean.write \
    .partitionBy("year", "month") \
    .mode("overwrite") \
    .parquet("s3a://silver/taxi/yellow/")

print(f"Silver complete: {df_clean.count():,} rows")
spark.stop()