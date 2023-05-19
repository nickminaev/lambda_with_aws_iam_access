terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.9.0"
    }
  }
  required_version = "~> 1.0"
}

provider "aws" {
  region = "eu-west-1"
}


resource "aws_iam_role" "iam_for_lambda" {
  name = "iam_for_lambda"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Sid    = ""
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_lambda_function" "lambda_tutorial" {
  filename         = "package.zip"
  function_name    = "tutorial"
  role             = aws_iam_role.iam_for_lambda.arn
  handler          = "lambda_function.lambda_handler"
  source_code_hash = filebase64sha256("package.zip")
  runtime          = "python3.9"
}

resource "aws_lambda_function_url" "lambda_tutorial_url" {
  function_name      = aws_lambda_function.lambda_tutorial.arn
  authorization_type = "AWS_IAM"
}

resource "aws_iam_user" "lambda_invoker" {
  name = "lambda_invoker"
}

resource "aws_iam_access_key" "lambda_invoker_key" {
  user    = aws_iam_user.lambda_invoker.name
}

resource "aws_iam_role" "function_invoker" {
  name = "function_invoker"
  assume_role_policy = jsonencode(
    {
        Version = "2012-10-17"
        Statement = [{
            Sid      = ""
            Effect   = "Allow"
            Action   = "sts:AssumeRole"
            Principal = {
              AWS = aws_iam_user.lambda_invoker.arn
            }
        }]
    })
}

resource "aws_iam_policy" "invoke_lambda_permissions" {
  name        = "InvokeSingleLambdaPolicy"
  description = "Custom policy for invoking Lambda functions and function URLs"

  policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [
      {
        Sid       = "AllowInvokeFunction"
        Effect    = "Allow"
        Action    = [
          "lambda:InvokeFunction",
          "lambda:InvokeAsync",
        ]
        Resource  = aws_lambda_function.lambda_tutorial.arn
      },
      {
        Sid       = "AllowInvokeFunctionURL"
        Effect    = "Allow"
        Action    = [
          "lambda:InvokeFunctionURL",
        ]
        Resource  = aws_lambda_function.lambda_tutorial.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_invoker_role_policy_attachment" {
  role       = aws_iam_role.function_invoker.name
  policy_arn = aws_iam_policy.invoke_lambda_permissions.arn
}

output "function_invoker_access_key_id" {
  description = "Function invoker access key id"
  value       = aws_iam_access_key.lambda_invoker_key.id
}

output "function_invoker_access_key" {
  description = "Function invoker access key"
  value       = aws_iam_access_key.lambda_invoker_key.secret
  sensitive   = true
}

output "function_invoker_role" {
  description = "Function invoker ARN"
  value       = aws_iam_role.function_invoker.arn
}

output "function_url" {
  description = "Function URL."
  value       = aws_lambda_function_url.lambda_tutorial_url.function_url
}



