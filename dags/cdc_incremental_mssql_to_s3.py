# dags/sqlserver_dump_full_or_cdc_ct.py
from __future__ import annotations
from airflow.decorators import dag, task
from airflow.providers.microsoft.mssql.hooks.mssql import MsSqlHook
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from datetime import datetime, timezone
import csv, json, tempfile

# -----------------------------
# CONFIG SIMPLES
# -----------------------------
MSSQL_CONN_ID = "mssql_local"
AWS_CONN_ID   = "aws_default"
S3_BUCKET     = "meu-bucket-dados"          # ajuste
S3_PREFIX     = "raw/sqlserver"              # ajuste
FETCH_SIZE    = 50_000

TABLES = [
    {"table": "dbo.clientes", "capture_instance": "dbo_clientes"},
    {"table": "dbo.lojas",    "capture_instance": "dbo_lojas"},
    {"table": "dbo.pedidos",  "capture_instance": "dbo_pedidos"},
]

def full_marker_key(table: str) -> str:
    # s3://bucket/raw/sqlserver/dbo/clientes/_full_done.json
    return f"{S3_PREFIX}/{table.replace('.', '/')}/_full_done.json"

def out_key(table: str, mode: str, ts: str) -> str:
    # s3://bucket/raw/sqlserver/dbo/clientes/load_ts=YYYYMMDDTHHMMSS/<mode>.csv
    return f"{S3_PREFIX}/{table.replace('.', '/')}/load_ts={ts}/{mode}.csv"

@dag(
    dag_id="sqlserver_dump_full_or_cdc_ct",
    schedule="@hourly",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["etl", "sqlserver", "cdc", "s3", "minimal"]
)
def sqlserver_dump_full_or_cdc_ct():

    @task
    def run():
        mss = MsSqlHook(mssql_conn_id=MSSQL_CONN_ID)
        s3  = S3Hook(aws_conn_id=AWS_CONN_ID)

        load_ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")

        conn = mss.get_conn()

        for cfg in TABLES:
            table = cfg["table"]
            ci    = cfg["capture_instance"]

            # Se o marcador FULL não existe -> fazemos FULL, senão CDC CT
            marker = full_marker_key(table)
            has_full = s3.check_for_key(marker, bucket_name=S3_BUCKET)

            if not has_full:
                mode = "full"
                sql  = f"SELECT * FROM {table} WITH (NOLOCK);"
            else:
                mode = "cdc_ct"
                sql  = f"SELECT * FROM cdc.{ci}_CT WITH (NOLOCK);"  # sem filtros, pega tudo que está retido

            cur = conn.cursor()
            cur.execute(sql)
            cols = [c[0] for c in cur.description] if cur.description else []

            key = out_key(table, mode, load_ts)

            # grava em arquivo temporário e sobe de uma vez (baixa memória)
            with tempfile.NamedTemporaryFile(mode="w+", newline="", delete=False) as tmp:
                w = csv.writer(tmp)
                if cols:
                    w.writerow(cols)
                total = 0
                while True:
                    rows = cur.fetchmany(FETCH_SIZE)
                    if not rows:
                        break
                    w.writerows(rows)
                    total += len(rows)
                tmp.flush()
                s3.load_file(filename=tmp.name, key=key, bucket_name=S3_BUCKET, replace=True)

            cur.close()

            # Se foi a primeira execução (FULL), grava o marcador para próximas rodadas usarem CDC
            if not has_full:
                s3.load_string(
                    string_data=json.dumps({
                        "full_done_at": datetime.now(timezone.utc).isoformat(),
                        "table": table
                    }),
                    key=marker,
                    bucket_name=S3_BUCKET,
                    replace=True
                )

        conn.close()

    run()

sqlserver_dump_full_or_cdc_ct = sqlserver_dump_full_or_cdc_ct()
