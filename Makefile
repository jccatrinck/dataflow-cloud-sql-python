.PHONY: help

CURRENT_DIR := $(shell basename $(CURDIR))

DOCKER_IMAGE = gcr.io/${GCP_PROJECT_ID}/pipeline-${CURRENT_DIR}:latest

ifneq (,$(wildcard ./.env))
    include .env
    export
    ENV_FILE_PARAM = --env-file .env
endif

help: ## Show command list
	@ grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

install-dependencies: ## Install dependencies
	@ pip install apache_beam[gcp]
	@ pip install pg8000
	@ pip install psycopg2
	@ pip install sqlalchemy

docker-push: ## Push Dataflow docker container image to GCP
	docker build --tag ${DOCKER_IMAGE} \
		--build-arg CLOUD_SQL_INSTANCES=${CLOUD_SQL_INSTANCES} \
		--build-arg CREDENTIAL_FILE=${GCP_SERVICE_ACCOUNT_FILE} \
		--file ./devops/Dockerfile .
	docker push ${DOCKER_IMAGE}

deploy: ## Deploy pipeline template to Cloud Storage bucket
	@ python main.py \
		--runner DataflowRunner \
		--project ${GCP_PROJECT_ID} \
		--region ${GCP_REGION} \
		--temp_location gs://${GCP_BUCKET_NAME}/temp \
		--template_location gs://${GCP_BUCKET_NAME}/templates/${CURRENT_DIR} \
		--experiment=use_runner_v2 \
		--sdk_container_image=${DOCKER_IMAGE} \
		--service-account-file ${GCP_SERVICE_ACCOUNT_FILE} \
		--setup_file ./setup.py \
		--db-url ${DB_URL}