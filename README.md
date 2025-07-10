# Lakehouse Athena

Este repositório fornece um exemplo de stack "lakehouse" local usando **Apache Spark** e **MinIO** para armazenamento de objetos. É destinado a experimentos com Spark, tabelas Delta e armazenamento compatível com S3.

## Arquitetura

O diagrama a seguir ilustra como os contêineres se conectam para formar a stack.

![Arquitetura do projeto](image.png)

## Visão Geral do Repositório

- `docker-compose.yml` – orquestração dos serviços
- `config/` – modelos de configuração do Spark
- `images/` – Dockerfiles utilizados nas imagens
- `dags/` – DAGs de exemplo para o Airflow
- `jobs/` – notebooks e scripts de exemplo
- `makefile` – comandos de apoio para operação da stack

## Requisitos

- [Docker](https://docs.docker.com/get-docker/) com Docker Compose
- [make](https://www.gnu.org/software/make/) para executar o *makefile*

## Configuração Inicial

1. **Copie o arquivo `.env.example` para `.env`** e ajuste os valores abaixo se necessário:

   ```env
   MINIO_ROOT_USER=minio
   MINIO_ROOT_PASSWORD=miniopass
   MINIO_URI=http://minio:9000
   AWS_ACCESS_KEY_ID=$MINIO_ROOT_USER
   AWS_SECRET_ACCESS_KEY=$MINIO_ROOT_PASSWORD
   ```
   Esses valores são utilizados para gerar `config/spark-defaults.conf` e executar os contêineres.

2. **Inicie a stack**:

   ```bash
   make up
   ```
   O alvo `make up` verifica/cria a rede `datalake-network`, gera a configuração do Spark e sobe os serviços definidos no `docker-compose.yml`.

3. **Pare a stack**:

   ```bash
   make down
   ```

## Utilização

Acesse o Jupyter Notebook em [http://localhost:8888](http://localhost:8888). A autenticação vem desabilitada por padrão. Há um notebook de exemplo em `jobs/teste.ipynb` demonstrando a escrita de uma pequena tabela Delta no MinIO.

MinIO fica disponível em:

- **API**: `http://localhost:9000`
- **Console**: `http://localhost:9001`

Utilize as credenciais do arquivo `.env` para fazer login.

## Customização

- **Configuração do Spark**: edite `config/spark-defaults.conf.template` e execute `make build` ou `make up` para reconstruir.
- **Imagens Docker**: os Dockerfiles em `images/` podem ser adaptados para instalar dependências adicionais.
- **Jobs/Notebooks**: adicione seus notebooks ou scripts Spark em `jobs/`.

## Testes

Execute `pytest` para validar os DAGs e garantir que não há erros de importação.

## Licença

Este projeto é fornecido "no estado em que se encontra" para fins educacionais.
