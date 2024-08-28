variable "schedule_expression" {
  default     = "cron(5 * * * ? *)"
  description = "the aws cloudwatch event rule schedule expression that specifies when the scheduler runs. Default is 5 minuts past the hour. for debugging use 'rate(5 minutes)'. See https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/ScheduledEvents.html"
}
