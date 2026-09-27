# IAM Target Matrix

## Overview

This document defines the target IAM model for this project: who acts,
which IAM identity they use, what they can do, and on which resources.
It is the security contract before encoding identities in Terraform.

## Status legend

- **Active** — already present and working in AWS as described
- **Pending** — target design not yet applied

## Actors

| Actor | IAM identity | What it can do | On which resource | Status |
|--------|--------------|----------------|-------------------|--------|
| **You** | `lakehouse-admin` (IAM User) | Manage project infrastructure | Project resources in `eu-north-1` (+ IAM, which is global) | Active |
| **Lambda `github-ingestion-s3-bronze`** | `lambda-github-ingestion-role` (IAM Role) | Write logs | `arn:aws:logs:eu-north-1:551322108190:log-group:/aws/lambda/github-ingestion-s3-bronze:*` | Active |
| ↑ | ↑ | Read and write S3 objects | `arn:aws:s3:::event-driven-lakehouse-bronze/*` | Active |
| ↑ | ↑ | Read the secret | `arn:aws:secretsmanager:eu-north-1:551322108190:secret:github-events-ingestion/token-*` | Pending |
| **Scheduler `daily-github-events-ingestion`** | `Amazon_EventBridge_Scheduler_LAMBDA_0d418f8cf4` (IAM Role) | Invoke the Lambda | `arn:aws:lambda:eu-north-1:551322108190:function:github-ingestion-s3-bronze:*` | Active |

## Trust

Each service role can be assumed only by its AWS service:

- `lambda-github-ingestion-role` — `lambda.amazonaws.com`
- `Amazon_EventBridge_Scheduler_LAMBDA_0d418f8cf4` — `scheduler.amazonaws.com`, limited to account `551322108190`

## Diagram

```
You (lakehouse-admin) ──► Terraform / Console / CLI

Scheduler ──invoke──► Lambda
                         │
                         ├── s3:::event-driven-lakehouse-bronze/*
                         ├── secretsmanager …/github-events-ingestion/token  [pending]
                         └── logs …/github-ingestion-s3-bronze
```

## Out of scope

- Fine-grained admin policy document (resolved when writing Terraform)
- Renaming the Scheduler role
- Glue, Athena, dbt, Airflow, and CI deploy identities
