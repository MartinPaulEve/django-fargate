output "registry_nginx_url" {
  value = aws_ecr_repository.nginx.repository_url
}

output "registry_nginx_arn" {
  value = aws_ecr_repository.nginx.arn
}


output "registry_python_url" {
  value = aws_ecr_repository.python.repository_url
}

output "registry_python_arn" {
  value = aws_ecr_repository.python.arn
}
