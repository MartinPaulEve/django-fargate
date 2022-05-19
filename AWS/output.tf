output "loadbalancer-address" {
  value = module.ecs-fargate-service.aws_lb_lb_dns_name
}

output "fargate_service_arn" {
  value     = module.ecs-fargate-service.aws_ecs_service_service_id
}

output "subnets" {
  value = module.ecs-fargate-service.subnets
}