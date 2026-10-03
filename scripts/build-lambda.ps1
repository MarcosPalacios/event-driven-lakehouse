# Original Lambda package build (from docs/lambda-deploy.md)
# Run from the repository root:
#   .\scripts\build-lambda.ps1

$ErrorActionPreference = "Stop"

Set-Location (Resolve-Path (Join-Path $PSScriptRoot ".."))

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

Write-Host "Done: $(Resolve-Path .\tmp-build\lambda.zip)"
