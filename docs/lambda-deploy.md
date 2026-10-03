# Lambda deployment

This document captures the workflow to package the Lambda and deploy it without
leaving build artifacts in git.

## Goal

Create a temporary zip containing the Lambda code and its dependencies, then
upload it to AWS. Prefer Terraform for deploy; AWS CLI remains as an alternative.

## Recommended structure

- Source code: `ingestion/`
- Temporary build folder: `tmp-build/`
- Final artifact: `tmp-build/lambda.zip`
- Build script: `scripts/build-lambda.ps1` (same steps as below)
- Clean repo: no `build/` folder and no zip in the root

## PowerShell commands

Run this from the project root:

```powershell
# 0) Clean previous build
Remove-Item .\tmp-build -Recurse -Force -ErrorAction SilentlyContinue

# 1) create a temporary build folder
New-Item -ItemType Directory -Force -Path .\tmp-build | Out-Null

# 2) copy the Lambda source code
Copy-Item -Recurse -Force .\ingestion .\tmp-build\

# 3) install runtime dependencies into the temporary folder
python -m pip install -r .\ingestion\lambda\requirements.txt -t .\tmp-build

# 4) create the final zip inside the temporary folder
Compress-Archive -Path .\tmp-build\* -DestinationPath .\tmp-build\lambda.zip -Force
```

Or:

```powershell
.\scripts\build-lambda.ps1
```

## Deploy with Terraform (recommended)

`terraform/lambda.tf` points at `tmp-build/lambda.zip`. After building the zip:

```powershell
cd terraform
terraform plan
terraform apply
```

Terraform updates the function when `source_code_hash` changes. Environment
variables (including `GITHUB_TOKEN`) are ignored by Terraform until Secrets Manager.

## Deploy with AWS CLI (alternative)

```powershell
aws lambda update-function-code `
  --function-name github-ingestion-s3-bronze `
  --zip-file fileb://.\tmp-build\lambda.zip
```

## Optional environment configuration

If the Lambda needs environment variables, update them with:

```powershell
aws lambda update-function-configuration `
  --function-name github-ingestion-s3-bronze `
  --environment "Variables={GITHUB_TOKEN=<token>,BRONZE_BUCKET=event-driven-lakehouse-bronze,GITHUB_OWNER=apache,GITHUB_REPO=spark}"
```

## Quick validation

```powershell
aws lambda invoke `
  --function-name github-ingestion-s3-bronze `
  --cli-binary-format raw-in-base64-out `
  --payload '{"source":"manual"}' `
  output.json

Get-Content .\output.json
```

## Optional cleanup

```powershell
Remove-Item -Recurse -Force .\tmp-build -ErrorAction SilentlyContinue
```

## Note

The `tmp-build` folder is included in `.gitignore` so it does not appear as a repository change.
