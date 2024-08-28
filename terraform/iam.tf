


# IAM Role for Lambda function

data "aws_iam_policy_document" "lambda" {
  statement {
    sid    = "ec2Role"
    effect = "Allow"
    actions = [
      "sts:AssumeRole"
    ]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "scheduler_lambda" {
  name               = "scheduler_lambda"
  assume_role_policy = data.aws_iam_policy_document.lambda.json
}

data "aws_iam_policy_document" "ec2-access-scheduler" {
  statement {
    actions = [
      "ec2:DescribeInstances",
      "ec2:StopInstances",
      "ec2:StartInstances",
      "ec2:CreateTags",
      "rds:DescribeDBInstances",
      "rds:DescribeDBClusters",
      "rds:StartDBInstance",
      "rds:StopDBInstance",
      "rds:ListTagsForResource",
      "rds:AddTagsToResource",
    ]
    resources = [
      "*",
    ]
  }
}

resource "aws_iam_policy" "ec2-access-scheduler" {
  name   = "ec2-access-scheduler"
  path   = "/"
  policy = data.aws_iam_policy_document.ec2-access-scheduler.json
}

resource "aws_iam_role_policy_attachment" "ec2-access-scheduler" {
  role       = aws_iam_role.scheduler_lambda.name
  policy_arn = aws_iam_policy.ec2-access-scheduler.arn
}

## create custom role

data "aws_iam_policy_document" "lambda-basic-scheduler" {
  statement {
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]
    resources = [
      "*",
    ]
  }
}

resource "aws_iam_policy" "scheduler_aws_lambda_basic_execution_role" {
  name        = "scheduler_aws_lambda_basic_execution_role"
  path        = "/"
  description = "AWSLambdaBasicExecutionRole"
  policy = data.aws_iam_policy_document.lambda-basic-scheduler.json

}

resource "aws_iam_role_policy_attachment" "basic-exec-role" {
  role       = aws_iam_role.scheduler_lambda.name
  policy_arn = aws_iam_policy.scheduler_aws_lambda_basic_execution_role.arn
}

