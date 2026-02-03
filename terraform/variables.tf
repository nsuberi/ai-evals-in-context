variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (e.g., prod, staging)"
  type        = string
  default     = "prod"
}

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "ai-testing-resource"
}

variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default     = "portfolio.cookinupideas.com"
}

variable "route53_zone_id" {
  description = "Route 53 hosted zone ID"
  type        = string
  default     = "Z0990573XMA6PHFKL82S"
}

variable "anthropic_api_key" {
  description = "Anthropic API key for Claude"
  type        = string
  sensitive   = true
}

# Container configuration
variable "container_cpu" {
  description = "CPU units for the container (256 = 0.25 vCPU)"
  type        = number
  default     = 256
}

variable "container_memory" {
  description = "Memory for the container in MB"
  type        = number
  default     = 512
}

variable "container_port" {
  description = "Port the container listens on"
  type        = number
  default     = 5000
}

# Database configuration
variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t4g.micro"
}

variable "db_allocated_storage" {
  description = "Allocated storage for RDS in GB"
  type        = number
  default     = 20
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "tsr_db"
}

variable "db_username" {
  description = "Database master username"
  type        = string
  default     = "tsr_user"
}

# VPC configuration
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Availability zones to use"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

# ACM Certificate for ALB HTTPS
variable "certificate_arn" {
  description = "ACM certificate ARN for HTTPS (reuse existing from proto-portal)"
  type        = string
  default     = "arn:aws:acm:us-east-1:671388079324:certificate/4240573d-1c6a-44ec-9eee-eedc5f4c9157"
}
