# Terraform

Declarative infrastructure for the event-driven lakehouse (region `eu-north-1`).

## Current status (2026-10-03)

Managed in Terraform:

- Layout: `versions.tf`, `providers.tf`, `iam.tf`, `s3.tf`, `lambda.tf`, `scheduler.tf`, `outputs.tf`
- IAM user `lakehouse-admin` (`AdministratorAccess`)
- S3 `event-driven-lakehouse-bronze` (+ encryption, public access block) — imported
- Lambda `github-ingestion-s3-bronze` + role `lambda-github-ingestion-role` — imported; function code deployed from `tmp-build/lambda.zip` (see [docs/lambda-deploy.md](../docs/lambda-deploy.md)); env vars (including `GITHUB_TOKEN`) still ignored by Terraform until Secrets Manager
- Scheduler `daily-github-events-ingestion` + role `scheduler-github-ingestion-role` — managed in Terraform (schedule recreated with a clean role name)
- Auth: AWS CLI profile `lakehouse-admin` in `providers.tf`

## How to run

Package the Lambda first (from the repo root), then plan/apply:

```powershell
.\scripts\build-lambda.ps1
cd terraform
terraform plan
terraform apply
```

`terraform plan` / `apply` require `tmp-build/lambda.zip` to exist when managing the function code.

## Environment note (Windows + Avast)

Avast HTTPS scanning breaks the Terraform AWS provider plugin
(`x509: certificate signed by unknown authority` / failed to load plugin schemas).
File/Command exclusions are not enough. Workaround: disable Web Shield → HTTPS
scanning only while running Terraform, then re-enable it.

## Pending (next sessions)

1. Replace `AdministratorAccess` with a least-privilege project policy
2. Secrets Manager for the GitHub token + Lambda role permission (per IAM matrix); stop storing the token in Lambda environment variables
3. Optional later: remote state, MFA on `lakehouse-admin`, SSO/Identity Center

## Layout

Resources are split by domain:

| File | Contents |
|------|----------|
| `iam.tf` | `lakehouse-admin`, Lambda role, Scheduler role |
| `s3.tf` | Bronze bucket + encryption + public access block |
| `lambda.tf` | Ingestion function |
| `scheduler.tf` | Daily EventBridge Scheduler schedule |
| `outputs.tf` | Useful ARNs / names |
| `versions.tf` / `providers.tf` | Terraform + AWS provider |
