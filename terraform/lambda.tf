# AWS Lambda need a zip file
data "archive_file" "aws-scheduler" {
  type        = "zip"
  source_dir  = "${path.module}/src"
  output_path = "${path.module}/aws-scheduler.zip"
}

# AWS Lambda function
resource "aws_lambda_function" "scheduler_lambda" {
  filename         = data.archive_file.aws-scheduler.output_path
  function_name    = "aws-scheduler"
  role             = aws_iam_role.scheduler_lambda.arn
  handler          = "aws-scheduler.handler"
  runtime          = "python3.11"
  timeout          = 300
  source_code_hash = data.archive_file.aws-scheduler.output_base64sha256


  environment {
    variables = {
      # EC2_SCHEDULE            = var.ec2_schedule
      LOG_LEVEL = "INFO"
    }
  }

  lifecycle {
    ignore_changes = [ environment.0.variables["LOG_LEVEL"], ]
  }
}

resource "aws_lambda_permission" "allow_cloudwatch_to_call_scheduler" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.scheduler_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.check-scheduler-event.arn
}
