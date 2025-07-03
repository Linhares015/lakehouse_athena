ENV_FILE = .env
SPARK_DEFAULTS_TEMPLATE_PATH = config/spark-defaults.conf.template
SPARK_DEFAULTS_PATH = config/spark-defaults.conf
NETWORK_NAME=lakehouse-athena_524485_airflow

include $(ENV_FILE)
export $(shell sed 's/=.*//' $(ENV_FILE))


.PHONY: create-network
create-network:
	@if ! docker network inspect $(NETWORK_NAME) > /dev/null 2>&1; then \
		echo "🔧 Criando rede $(NETWORK_NAME)..."; \
		docker network create $(NETWORK_NAME); \
	else \
		echo "✅ Rede $(NETWORK_NAME) já existe."; \
	fi


.PHONY: build
build: create-network
	envsubst < $(SPARK_DEFAULTS_TEMPLATE_PATH) > $(SPARK_DEFAULTS_PATH)

.PHONY: up
up: build
	@echo "🚀 Iniciando os containers..."
	astro dev start
	docker compose up --build -d


.PHONY: down
down:
	@echo "🛑 Parando os containers..."
	astro dev stop
	docker compose down
	docker network rm $(NETWORK_NAME)