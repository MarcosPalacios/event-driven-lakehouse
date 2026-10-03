resource "aws_scheduler_schedule" "daily_github_ingestion" {
  name       = "daily-github-events-ingestion"
  group_name = "default"
  state      = "ENABLED"

  schedule_expression          = "cron(0 9 * * ? *)"
  schedule_expression_timezone = "Europe/Madrid"

  flexible_time_window {
    mode = "OFF"
  }

  target {
    arn      = aws_lambda_function.github_ingestion.arn
    role_arn = aws_iam_role.scheduler_github_ingestion.arn

    retry_policy {
      maximum_retry_attempts       = 0
    }
  }
}
