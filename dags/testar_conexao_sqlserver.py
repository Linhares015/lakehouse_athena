# dags/testar_conexao_sqlserver_hook.py

from airflow import DAG
from airflow.decorators import task
from airflow.providers.microsoft.mssql.hooks.mssql import MsSqlHook
from datetime import datetime

with DAG(
    dag_id="testar_conexao_sqlserver_hook",
    schedule=None,
    start_date=datetime(2025,1,1),
    catchup=False,
    tags=["test","mssql"]
) as dag:

    @task()
    def teste_hook():
        hook = MsSqlHook(mssql_conn_id="mssql_local")
        result = hook.get_records("SELECT 1 AS test_connection")
        print("Resultado da conexão:", result)

    teste_hook()
