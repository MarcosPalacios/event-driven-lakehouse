# Terraform

Declarative infrastructure for the event-driven lakehouse (region `eu-north-1`).

## Current status (2026-09-27)

In AWS / Terraform today:

- Scaffold: `versions.tf`, `providers.tf` (profile `lakehouse-admin`), `main.tf`
- IAM user `lakehouse-admin` with managed policy `AdministratorAccess` (managed in TF)
- Local auth: AWS CLI profile `lakehouse-admin` (access keys in `~/.aws/credentials`)
- Provider uses `profile = "lakehouse-admin"` — no `export-credentials` needed for Terraform

Still **manual in AWS** (not in TF yet): S3 bronze, Lambda `github-ingestion-s3-bronze`, EventBridge Scheduler, Lambda execution role, Scheduler role.

## How to run

```powershell
cd terraform
terraform plan
terraform apply
```

## Environment note (Windows + Avast)

Avast HTTPS scanning breaks the Terraform AWS provider plugin
(`x509: certificate signed by unknown authority` / failed to load plugin schemas).
File/Command exclusions are not enough. Workaround: disable Web Shield → HTTPS
scanning only while running Terraform, then re-enable it.

## Pending (next sessions)

1. Replace `AdministratorAccess` with a least-privilege project policy
2. Decide import vs recreate, then migrate S3 / Lambda / Scheduler (and related IAM roles) into Terraform
3. Lambda: Secrets Manager permission for the GitHub token (per IAM matrix)
4. Optional later: remote state, MFA on `lakehouse-admin`, SSO/Identity Center

## Layout note

Keep resources in `main.tf` for now; split by domain (`iam.tf`, `s3.tf`, …) when the config grows.
