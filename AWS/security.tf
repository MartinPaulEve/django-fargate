resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy_attach" {
  role       = module.td.aws_iam_role_ecs_task_execution_role_name
  policy_arn = "arn:aws:iam::aws:policy/SecretsManagerReadWrite"
}

resource "aws_iam_policy" "ecs_task_execution_role_custom_policy" {
  name        = "${var.name_prefix}-ecs-task-execution-role-exec-policy"
  description = "An execution policy for ${var.name_prefix}-ecs-task-execution-role IAM Role"
  policy      = "{\"Version\": \"2012-10-17\", \"Statement\": [ {\"Effect\": \"Allow\", \"Action\": [\"ssmmessages:CreateControlChannel\", \"ssmmessages:CreateDataChannel\", \"ssmmessages:OpenControlChannel\", \"ssmmessages:OpenDataChannel\"], \"Resource\": \"*\" }] }"
  tags        = var.tags
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_exec_role_policy_attach" {
  role       = module.td.aws_iam_role_ecs_task_execution_role_name
  policy_arn = aws_iam_policy.ecs_task_execution_role_custom_policy.arn
}
