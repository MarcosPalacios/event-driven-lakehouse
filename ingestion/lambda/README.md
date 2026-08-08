# Lambda

## Overview

This module contains the AWS Lambda entrypoint for the ingestion pipeline.
It is designed to call the existing Bronze ingestion logic in `ingestion/main.py`.

## What it does

- Provides a lightweight Lambda handler at `ingestion/lambda/handler.py`
- Reuses `run_ingestion` from `ingestion/main.py`
- Runs against the default repository `apache/spark`
- Reads configuration from environment variables
- Returns the ingestion result as a JSON body

## What it does not do

- Does not implement Bronze → Silver transformation
- Does not perform Parquet conversion
- Does not include Lambda deployment or infrastructure
- Does not parse event payloads from API Gateway or S3 triggers

## Configuration

The handler expects the following environment variables:

- `GITHUB_TOKEN` (required)
- `BRONZE_BUCKET` (defaults to `event-driven-lakehouse-bronze`)
- `CHECKPOINT_BUCKET` (defaults to the Bronze bucket)
- `GITHUB_OWNER` (defaults to `apache`)
- `GITHUB_REPO` (defaults to `spark`)

## Local usage

The handler is intended to be invoked by AWS Lambda.
For local testing, call `run_ingestion` from `ingestion/main.py` directly with the same environment variables.

## Current status

### Implemented

- `ingestion/lambda/handler.py` created as the Lambda entrypoint.
- Handler imports `run_ingestion` from `ingestion/main.py`.
- Defaults to `apache/spark`.
- Reads env vars for GitHub token, Bronze bucket, and checkpoint bucket.
- Keeps the Lambda handler minimal and reusable.
- **Packaging and deployment from CLI via AWS CLI** (see [docs/lambda-deploy.md](../../docs/lambda-deploy.md) for the full workflow)

### Pending

- Configure S3 or HTTP triggers to invoke the handler
- Add actual Bronze → Silver transformation or Parquet output
- Add Lambda-specific unit and integration tests
- Add infrastructure code for the function and permissions in Terraform
