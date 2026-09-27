data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

resource "aws_iam_user" "lakehouse_admin" {
  name = "lakehouse-admin"
}

resource "aws_iam_user_policy_attachment" "lakehouse_admin" {
  user       = aws_iam_user.lakehouse_admin.name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}

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