# lakehouse_athena

Este projeto demonstra um ambiente de Lakehouse on-premises utilizando Docker Compose com os seguintes componentes:

- **MinIO** como storage compatível com S3
- **Hive Metastore** com banco PostgreSQL
- **Spark** com suporte a Delta Lake (master e worker)
- **Trino** configurado para acessar o Hive Metastore e o MinIO

## Estrutura de diretórios

- `minio/data` – volume persistente do MinIO
- `postgres/data` – volume do PostgreSQL usado pelo Hive Metastore
- `spark/conf` – configurações do Spark (ex.: `spark-defaults.conf`)
- `trino/catalog` – catálogos do Trino
- `scripts` – utilitários para iniciar ou parar o ambiente

## Uso

Para iniciar todos os serviços em segundo plano utilize o script:

```bash
./scripts/start.sh
```

A interface do MinIO estará disponível em `http://localhost:9001` (usuário `minio` / senha `minio123`).
O Spark Master estará em `http://localhost:8080` e o Trino em `http://localhost:8088`.

Quando quiser interromper e remover os serviços execute:

```bash
./scripts/stop.sh
```
