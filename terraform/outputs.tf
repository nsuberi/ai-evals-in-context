output "api_gateway_url" {
  description = "API Gateway endpoint URL (use this for CloudFront origin)"
  value       = module.api_gateway.api_endpoint
}

output "api_gateway_domain" {
  description = "API Gateway domain name (for CloudFront origin configuration)"
  value       = module.api_gateway.api_domain
}

output "ecr_repository_url" {
  description = "ECR repository URL for Docker images"
  value       = module.ecs.ecr_repository_url
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = module.ecs.cluster_name
}

output "ecs_service_name" {
  description = "ECS service name"
  value       = module.ecs.service_name
}

output "rds_endpoint" {
  description = "RDS PostgreSQL endpoint"
  value       = module.database.db_endpoint
}

output "cloudwatch_log_group" {
  description = "CloudWatch log group for ECS tasks"
  value       = module.ecs.log_group_name
}

output "vpc_id" {
  description = "VPC ID"
  value       = module.networking.vpc_id
}

# ALB outputs
output "alb_dns_name" {
  description = "ALB DNS name (use this for CloudFront origin)"
  value       = module.alb.alb_dns_name
}

output "alb_zone_id" {
  description = "ALB zone ID for Route 53 alias records"
  value       = module.alb.alb_zone_id
}
