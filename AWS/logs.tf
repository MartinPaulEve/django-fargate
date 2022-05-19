resource "aws_cloudwatch_log_group" "container-log" {
  name = "container-log"

  tags = {
    Environment = "production"
    Application = "djangoTest"
  }
}