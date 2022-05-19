module "container-django-app-gunicorn" {
  source                       = "registry.terraform.io/cloudposse/ecs-container-definition/aws"
  version                      = "0.58.1"
  container_name               = "django_python"
  container_image              = "${data.aws_caller_identity.current.account_id}.dkr.ecr.us-east-1.amazonaws.com/djangotestpython"
  container_memory             = var.container_memory
  container_memory_reservation = var.container_memory_reservation
  entrypoint                   = var.entrypoint
  essential                    = true
  log_configuration            = var.log_configuration
  secrets                      = [{ "name" = "db_creds", "valueFrom" = "${aws_secretsmanager_secret.secret_main_db.arn}" }]
  port_mappings = [
    {
      "containerPort" : 8011,
      "hostPort" : 8011,
      "protocol" : "tcp"
    },
  ]
}

module "container-nginx" {
  source                       = "registry.terraform.io/cloudposse/ecs-container-definition/aws"
  version                      = "0.58.1"
  container_name               = "django_nginx"
  container_image              = "${data.aws_caller_identity.current.account_id}.dkr.ecr.us-east-1.amazonaws.com/djangotestnginx"
  depends_on                   = [module.container-django-app-gunicorn]
  container_memory             = var.container_memory
  container_memory_reservation = var.container_memory_reservation
  log_configuration            = var.log_configuration
  entrypoint                   = var.entrypoint
  essential                    = true
  secrets                      = [{ "name" = "db_creds", "valueFrom" = "${aws_secretsmanager_secret.secret_main_db.arn}" }]
  port_mappings = [
    {
      "containerPort" : 80,
      "hostPort" : 80,
      "protocol" : "tcp"
    },
    {
      "containerPort" : 443,
      "hostPort" : 443,
      "protocol" : "tcp"
    }
  ]
  healthcheck = var.healthcheck
}
