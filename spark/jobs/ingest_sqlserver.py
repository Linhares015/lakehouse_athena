from pyspark.sql import SparkSession


def main():
    """Ingest data from SQL Server and write to Delta Lake"""
    spark = (
        SparkSession.builder.appName("SQLServerIngest")
        .config("spark.jars.packages", "com.microsoft.sqlserver:mssql-jdbc:10.2.0.jre8")
        .getOrCreate()
    )

    jdbc_url = (
        "jdbc:sqlserver://SQLSERVER_HOST:1433;databaseName=DB_NAME"
    )

    connection_properties = {
        "user": "YOUR_USER",
        "password": "YOUR_PASSWORD",
        "driver": "com.microsoft.sqlserver.jdbc.SQLServerDriver",
    }

    table = "dbo.your_table"

    df = spark.read.jdbc(url=jdbc_url, table=table, properties=connection_properties)

    (
        df.write.format("delta")
        .mode("overwrite")
        .save("s3a://lakehouse/sqlserver/your_table")
    )

    spark.stop()


if __name__ == "__main__":
    main()
