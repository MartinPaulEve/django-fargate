# Create a random generated password to use in secrets.
# Note that we should NOT use special characters here as it messes with postgres
resource "random_password" "password" {
  length           = 16
  special          = false
}

# AWS secret for database master account
resource "aws_secretsmanager_secret" "secret_main_db" {
  name = var.secret_name
}

# AWS secret version for database account
resource "aws_secretsmanager_secret_version" "creds" {
  secret_id = aws_secretsmanager_secret.secret_main_db.id
  secret_string = jsonencode({
    username   = var.database_user,
    database   = module.aurora_postgresql.cluster_database_name,
    password   = module.aurora_postgresql.cluster_master_password
    production = random_string.django_production.result,
    host       = module.aurora_postgresql.cluster_endpoint,
    port       = module.aurora_postgresql.cluster_port
  })
  depends_on = [module.aurora_postgresql]
}

data "aws_secretsmanager_secret" "secret_main_db" {
  arn = aws_secretsmanager_secret.secret_main_db.arn
}

# django production
resource "random_string" "django_production" {

  length           = 16
  special          = false
}
