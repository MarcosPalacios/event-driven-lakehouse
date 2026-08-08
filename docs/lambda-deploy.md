# Lambda deployment from CLI

This document captures the recommended workflow to package the Lambda and deploy it from the terminal without leaving build artifacts in the project root.

## Goal

Create a temporary zip containing the Lambda code and its dependencies, upload it to AWS with the AWS CLI, and keep the repository clean.

## Recommended structure

- Source code: `ingestion/`
- Temporary build folder: `tmp-build/`
- Final artifact: `tmp-build/lambda.zip`
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

## Deploy with AWS CLI

Make sure the AWS CLI is installed and configured with valid credentials.

```powershell
aws lambda update-function-code \
  --function-name <name-of-your-lambda> \
  --zip-file fileb://.\tmp-build\lambda.zip
```

## Optional environment configuration

If the Lambda needs environment variables, update them with:

```powershell
aws lambda update-function-configuration \
  --function-name <name-of-your-lambda> \
  --environment "Variables={GITHUB_TOKEN=<token>,BRONZE_BUCKET=event-driven-lakehouse-bronze,GITHUB_OWNER=apache,GITHUB_REPO=spark}"
```

## Quick validation

Invoke the function from AWS:

```powershell
aws lambda invoke \
  --function-name <name-of-your-lambda> \
  --payload '{"source":"manual"}' \
  output.json
```

Then read the result:

```powershell
Get-Content .\output.json
```

## Optional cleanup

When you want the repo clean again:

```powershell
Remove-Item -Recurse -Force .\tmp-build -ErrorAction SilentlyContinue
```

## Note

The `tmp-build` folder is included in `.gitignore` so it does not appear as a repository change.
