resource "aws_iam_user" "lakehouse_admin" {
  name = "lakehouse-admin"
}

resource "aws_iam_user_policy_attachment" "lakehouse_admin" {
  user       = aws_iam_user.lakehouse_admin.name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}

resource "aws_iam_role" "lambda_github_ingestion" {
  name        = "lambda-github-ingestion-role"
  description = "Allows Lambda functions to call AWS services on your behalf."

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_github_ingestion_basic" {
  role       = aws_iam_role.lambda_github_ingestion.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "lambda_github_ingestion_s3" {
  name = "s3-bronze-read-write"
  role = aws_iam_role.lambda_github_ingestion.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "BronzeObjectReadWrite"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
        ]
        Resource = "${aws_s3_bucket.bronze.arn}/*"
      }
    ]
  })
}

resource "aws_iam_role" "scheduler_github_ingestion" {
  name        = "scheduler-github-ingestion-role"
  description = "Allows EventBridge Scheduler to invoke the GitHub ingestion Lambda."

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "scheduler.amazonaws.com"
        }
        Action = "sts:AssumeRole"
        Condition = {
          StringEquals = {
            "aws:SourceAccount" = data.aws_caller_identity.current.account_id
          }
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "scheduler_github_ingestion_invoke" {
  name = "lambda-invoke-github-ingestion"
  role = aws_iam_role.scheduler_github_ingestion.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "InvokeGithubIngestionLambda"
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction",
        ]
        Resource = [
          aws_lambda_function.github_ingestion.arn,
          "${aws_lambda_function.github_ingestion.arn}:*",
        ]
      }
    ]
  })
}
