data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

output "account_id" {
  value = data.aws_caller_identity.current.account_id
}

output "caller_arn" {
  value = data.aws_caller_identity.current.arn
}

output "region" {
  value = data.aws_region.current.name
}

output "lakehouse_admin_user_arn" {
  value = aws_iam_user.lakehouse_admin.arn
}

output "bronze_bucket_name" {
  value = aws_s3_bucket.bronze.bucket
}

output "bronze_bucket_arn" {
  value = aws_s3_bucket.bronze.arn
}

output "lambda_github_ingestion_name" {
  value = aws_lambda_function.github_ingestion.function_name
}

output "lambda_github_ingestion_arn" {
  value = aws_lambda_function.github_ingestion.arn
}

output "lambda_github_ingestion_role_arn" {
  value = aws_iam_role.lambda_github_ingestion.arn
}

output "scheduler_daily_github_ingestion_arn" {
  value = aws_scheduler_schedule.daily_github_ingestion.arn
}

output "scheduler_github_ingestion_role_arn" {
  value = aws_iam_role.scheduler_github_ingestion.arn
}
