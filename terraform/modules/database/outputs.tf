output "db_endpoint" {
  description = "RDS endpoint (hostname only, without port)"
  value       = aws_db_instance.main.address
}

output "db_port" {
  description = "RDS port"
  value       = aws_db_instance.main.port
}

output "db_password_secret_arn" {
  description = "ARN of the Secrets Manager secret containing the DB password"
  value       = aws_secretsmanager_secret.db_password.arn
}

output "db_instance_id" {
  description = "RDS instance ID"
  value       = aws_db_instance.main.id
}
