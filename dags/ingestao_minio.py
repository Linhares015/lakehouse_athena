from airflow.decorators import dag, task
from datetime import datetime
import boto3

@dag(
    dag_id="ingestao_minio_taskflow",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=["minio", "ingestao"]
)

def ingestao_minio():
    @task()
    def upload_to_minio():
        # Parâmetros da conexão (pode usar Variables/Connections se preferir)
        endpoint_url = "http://minio:9000"
        aws_access_key_id = "minioadmin"
        aws_secret_access_key = "minioadmin"
        bucket_name = "raw"
        local_file = "/usr/local/airflow/dags/teste.csv"
        s3_key = "teste.csv"

        s3 = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

        s3.upload_file(local_file, bucket_name, s3_key)
        print(f"Arquivo {local_file} enviado para {bucket_name}/{s3_key} no MinIO com sucesso!")

    upload_to_minio()

ingestao_minio_dag = ingestao_minio()
