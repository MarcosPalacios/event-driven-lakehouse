# Event-Driven Lakehouse

Practical project focused on a modern data platform on AWS with a Bronze/Silver/Gold architecture.

## Objective

Build a solution with:

- Incremental and idempotent ingestion from GitHub Events
- Storage in S3 Bronze/Silver/Gold
- Serverless processing with Lambda
- Query layer with Athena
- Transformations with dbt
- Orchestration with Airflow
- Declarative infrastructure with Terraform
- Observability with CloudWatch

## AWS Configuration

The project AWS region is `eu-north-1` (Europe, Stockholm).

## Repository Structure

```
event-driven-lakehouse/
│
├── ingestion/
│   └── lambda/
├── dbt/
├── airflow/
├── terraform/
├── docs/
├── tests/
└── README.md
```

## Next Steps

- [x] 1. **Ingestion Design:** Define the incremental ingestion flow and GitHub events structure.
- [x] 2. **Script Development:** Prototype the script in `ingestion/` to download and save JSONL to S3 Bronze.
- [x] 3. **Serverless Deployment:** Develop and deploy the Lambda function with EventBridge for automated ingestion.
- [ ] 4. **Security & Infrastructure (Terraform):** Stop using the *root* user. Create least-privilege IAM roles and migrate the current infrastructure (S3, Lambda, EventBridge) to `terraform/` to ensure portability across AWS accounts.
- [ ] 5. **PySpark Processing (Silver Layer):** Create an AWS Glue (PySpark) job to read the JSONL data from Bronze, clean it, deduplicate it, and partition it into columnar format (Parquet) in S3 Silver.
- [ ] 6. **Catalog & Queries:** Configure AWS Glue Data Catalog (Crawlers) and Amazon Athena to make Silver data queryable via SQL.
- [ ] 7. **Transformations (Gold Layer):** Create dbt models connected to Athena to generate aggregated tables, metrics, and data quality tests.
- [ ] 8. **Orchestration:** Add Airflow DAGs in `airflow/` to coordinate the end-to-end pipeline (Lambda -> Glue Job -> dbt runs).
- [ ] 9. **Documentation:** Document the final design, architecture diagrams, and technical decisions in `docs/`.