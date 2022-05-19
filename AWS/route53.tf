resource "aws_route53_record" "subdomain" {
  name    = "staging"
  zone_id = var.hosted_zone_id
  type    = "A"

  alias {
    name                   = module.ecs-fargate-service.aws_lb_lb_dns_name
    zone_id                = module.ecs-fargate-service.aws_lb_lb_zone_id
    evaluate_target_health = true
  }
}

