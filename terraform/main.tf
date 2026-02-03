# AI Testing Resource - Main Terraform Configuration
# Composes all modules for ECS Fargate deployment

locals {
  name_prefix = "${var.app_name}-${var.environment}"
}

# Networking: VPC, subnets, security groups
module "networking" {
  source = "./modules/networking"

  name_prefix        = local.name_prefix
  vpc_cidr           = var.vpc_cidr
  availability_zones = var.availability_zones
  container_port     = var.container_port
}

# Database: RDS PostgreSQL with Secrets Manager
module "database" {
  source = "./modules/database"

  name_prefix         = local.name_prefix
  vpc_id              = module.networking.vpc_id
  private_subnet_ids  = module.networking.private_subnet_ids
  db_security_group_id = module.networking.db_security_group_id

  db_instance_class    = var.db_instance_class
  db_allocated_storage = var.db_allocated_storage
  db_name              = var.db_name
  db_username          = var.db_username
}

# Store Anthropic API key in Secrets Manager
resource "aws_secretsmanager_secret" "anthropic_api_key" {
  name                    = "${local.name_prefix}/anthropic-api-key"
  recovery_window_in_days = 0  # Allow immediate deletion for dev
}

resource "aws_secretsmanager_secret_version" "anthropic_api_key" {
  secret_id     = aws_secretsmanager_secret.anthropic_api_key.id
  secret_string = var.anthropic_api_key
}

# ALB: Application Load Balancer for reliable connectivity
module "alb" {
  source = "./modules/alb"

  name_prefix           = local.name_prefix
  vpc_id                = module.networking.vpc_id
  public_subnet_ids     = module.networking.public_subnet_ids
  container_port        = var.container_port
  certificate_arn       = var.certificate_arn
  ecs_security_group_id = module.networking.ecs_security_group_id
}

# ECS: Cluster, task definition, service
module "ecs" {
  source = "./modules/ecs"

  name_prefix           = local.name_prefix
  vpc_id                = module.networking.vpc_id
  public_subnet_ids     = module.networking.public_subnet_ids
  ecs_security_group_id = module.networking.ecs_security_group_id

  container_cpu    = var.container_cpu
  container_memory = var.container_memory
  container_port   = var.container_port

  # Database connection
  db_host     = module.database.db_endpoint
  db_port     = module.database.db_port
  db_name     = var.db_name
  db_username = var.db_username
  db_password_secret_arn = module.database.db_password_secret_arn

  # Anthropic API key
  anthropic_api_key_secret_arn = aws_secretsmanager_secret.anthropic_api_key.arn

  # ALB target group for load balancer registration
  target_group_arn = module.alb.target_group_arn
}

# API Gateway: HTTP API with VPC Link to ECS
module "api_gateway" {
  source = "./modules/api_gateway"

  name_prefix            = local.name_prefix
  vpc_id                 = module.networking.vpc_id
  vpc_link_subnet_ids    = module.networking.public_subnet_ids  # Use public subnets where ECS runs
  ecs_security_group_id  = module.networking.ecs_security_group_id
  cloud_map_service_arn  = module.ecs.cloud_map_service_arn
  container_port         = var.container_port
}
