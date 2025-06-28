from pyspark.sql import SparkSession
from pyspark.sql.utils import AnalysisException


def main():
    """Ingest data from Postgres using CDC via updated_at column"""
    spark = (
        SparkSession.builder.appName("PostgresCDCIngest")
        .config("spark.jars.packages", "org.postgresql:postgresql:42.7.2")
        .getOrCreate()
    )

    jdbc_url = "jdbc:postgresql://POSTGRES_HOST:5432/DB_NAME"
    connection_properties = {
        "user": "YOUR_USER",
        "password": "YOUR_PASSWORD",
        "driver": "org.postgresql.Driver",
    }

    table = "public.your_table"
    delta_path = "s3a://lakehouse/postgres/your_table"

    try:
        last_df = spark.read.format("delta").load(delta_path)
        last_ts = last_df.agg({"updated_at": "max"}).collect()[0][0]
    except AnalysisException:
        last_ts = "1970-01-01 00:00:00"

    query = f"(SELECT * FROM {table} WHERE updated_at > '{last_ts}') AS t"

    df = spark.read.jdbc(url=jdbc_url, table=query, properties=connection_properties)

    (df.write.format("delta").mode("append").save(delta_path))

    spark.stop()


if __name__ == "__main__":
    main()
