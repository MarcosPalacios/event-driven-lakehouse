# Project Documentation

## Goal

Build a practical Senior Data Engineer / Data Platform Engineer level project on AWS, including:

- Bronze / Silver / Gold architecture
- Data lakehouse on S3
- Incremental and idempotent ingestion from GitHub Events
- Serverless processing with Lambda
- Serverless querying with Athena
- Transformations with dbt on Athena
- Orchestration with Airflow
- Infrastructure as code with Terraform
- Basic observability with CloudWatch

## Repository Context

This repository is designed for a hands-on project focused on:

- Learning modern data patterns on AWS
- Practicing ingestion, transformation, storage, and orchestration
- Keeping costs low (<100€) using serverless services
- Building a realistic GitHub events use case

### Repository Structure

```
event-driven-lakehouse/
├── ingestion/   # Python scripts for incremental ingestion to S3 Bronze
├── lambda/      # AWS Lambda function for Bronze -> Silver transformation
├── dbt/         # dbt models and tests for Athena and Gold
├── airflow/     # orchestration DAGs
├── terraform/   # declarative AWS infrastructure
├── docs/        # project documentation and design
├── tests/       # unit and local integration tests
└── README.md    # main project guide
```

## Current Status

- Repository created locally and on GitHub
- Main branch renamed to `main`

## Project Scope

### Ingestion

- Consume real GitHub events using Python
- Store event batches in S3 Bronze as JSONL
- Ensure incremental and idempotent ingestion
- Accept duplicates in Bronze

### Event-driven Processing

- S3 Bronze triggers Lambda when a file arrives
- Lambda parses JSONL and converts it to tabular format
- Lambda writes Parquet to Silver
- Business logic separated from the AWS handler
- Logic designed to be testable locally

### Query Layer and dbt

- Athena queries data directly on S3
- dbt builds SQL models on Athena
- Gold is materialized on S3 as Parquet
- Include incremental models, tests, and deduplication

### Orchestration

- Airflow orchestrates ingestion, dbt runs, and tests
- It does not process data directly
- Include retries and backfills

### Infrastructure

- First use AWS Console to learn the setup
- Then migrate the infrastructure to Terraform
- Provision S3, IAM, Lambda, policies, and CloudWatch

### Observability

- CloudWatch Logs for Lambda and pipeline
- Structured logging
- Retries and basic alerts
