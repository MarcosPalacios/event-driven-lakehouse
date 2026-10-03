locals {
  lambda_zip_path = "${path.module}/../tmp-build/lambda.zip"
}

resource "aws_lambda_function" "github_ingestion" {
  function_name = "github-ingestion-s3-bronze"
  role          = aws_iam_role.lambda_github_ingestion.arn
  handler       = "ingestion.lambda.handler.lambda_handler"
  runtime       = "python3.12"
  timeout       = 60
  memory_size   = 128
  architectures = ["x86_64"]

  filename         = local.lambda_zip_path
  source_code_hash = filebase64sha256(local.lambda_zip_path)

  depends_on = [
    aws_iam_role_policy_attachment.lambda_github_ingestion_basic,
    aws_iam_role_policy.lambda_github_ingestion_s3,
  ]

  # Env vars (including GITHUB_TOKEN) stay out of Terraform until Secrets Manager.
  lifecycle {
    ignore_changes = [
      environment,
    ]
  }
}
