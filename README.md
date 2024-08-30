# terraform-aws-lambda-scheduler
Stop and start EC2 and RDS instances according to schedule via lambda and terraform.

# Overview

The scheduler looks at the schedule tag to see if it needs to stop or start and instance.
It works by setting a tag (default name schedule) to a string giving the stop and start time hour for each day.

A schedule tag for an EC2 instance is json and looks like:
```json
{"mon": {"start": 7, "stop": 19},"tue": {"start": 7, "stop": 19},"wed": {"start": [9, 22], "stop": 19},"thu": {"start": 7, "stop": [2,19]}, "fri": {"start": 7, "stop": 19}, "sat": {"start": 22}, "sun": {"stop": 7}}
```
If you want to handle multiple stop/starts per day, you will need to pass a list in square brackets in the start/stop schedule.

You can also use:
* 'daily' - all days of the week 
* 'business' as placeholder for monday - friday.
* 'weekend' as placeholder for sat - sun.

This allow a much smaller configuration in tags. If is needed for configurations
with multiple times for stoppping an instance, because a value
of a tag is limitted to 254 characters.


## Requirements

This module requires Terraform version `0.12.x` or newer.

## Dependencies

This module depends on a correctly configured [AWS Provider](https://www.terraform.io/docs/providers/aws/index.html) in your Terraform codebase.

## Usage

```
module "lambda-scheduler" {
  version = "0.1"
  schedule_expression = "cron(5 * * * ? *)"
  tag = "schedule"
  schedule_tag_force = "true"
  ec2_schedule = "true"
  rds_schedule = "true"
  default = "{\"weekdays\": {\"start\": [7], \"stop\": [19]}}"
  time = "Europe/London"
}
```
## variables

### schedule_expression
The aws cloudwatch event rule schedule expression that specifies when the scheduler runs.

Default = "cron(5 * * * ? *)"  i.e. 5 minuts past the hour. for debugging use "rate(5 minutes)" See [ScheduledEvents](https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/ScheduledEvents.html)

### TZ
Timezone to use for scheduler. Can be 'local', 'Europe/Lisbon' see pytz library for Options
