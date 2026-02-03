variable "name_prefix" {
  description = "Prefix for resource names"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "vpc_link_subnet_ids" {
  description = "Subnet IDs for VPC Link (should be same subnets as ECS tasks)"
  type        = list(string)
}

variable "ecs_security_group_id" {
  description = "Security group ID for ECS tasks (used by VPC Link)"
  type        = string
}

variable "cloud_map_service_arn" {
  description = "Cloud Map service ARN for service discovery"
  type        = string
}

variable "container_port" {
  description = "Port the container listens on"
  type        = number
}
