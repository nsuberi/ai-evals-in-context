# ECS Module - Cluster, Task Definition, Service with Fargate Spot

# ECR Repository
resource "aws_ecr_repository" "main" {
  name                 = "${var.name_prefix}"
  image_tag_mutability = "MUTABLE"
  force_delete         = true  # For dev - allows deletion even with images

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name = "${var.name_prefix}-ecr"
  }
}

# ECR Lifecycle Policy - Keep only last 5 images
resource "aws_ecr_lifecycle_policy" "main" {
  repository = aws_ecr_repository.main.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep only last 5 images"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 5
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "main" {
  name              = "/ecs/${var.name_prefix}"
  retention_in_days = 30

  tags = {
    Name = "${var.name_prefix}-logs"
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = var.name_prefix

  setting {
    name  = "containerInsights"
    value = "disabled"  # Disable for cost savings
  }

  tags = {
    Name = "${var.name_prefix}-cluster"
  }
}

# ECS Cluster Capacity Providers (Fargate Spot)
resource "aws_ecs_cluster_capacity_providers" "main" {
  cluster_name = aws_ecs_cluster.main.name

  capacity_providers = ["FARGATE_SPOT", "FARGATE"]

  default_capacity_provider_strategy {
    capacity_provider = "FARGATE_SPOT"
    weight            = 100
    base              = 0
  }
}

# IAM Role for ECS Task Execution
resource "aws_iam_role" "ecs_task_execution" {
  name = "${var.name_prefix}-ecs-task-execution"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Allow ECS to read secrets from Secrets Manager
resource "aws_iam_role_policy" "ecs_secrets" {
  name = "${var.name_prefix}-ecs-secrets"
  role = aws_iam_role.ecs_task_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          var.db_password_secret_arn,
          var.anthropic_api_key_secret_arn
        ]
      }
    ]
  })
}

# IAM Role for ECS Task (runtime)
resource "aws_iam_role" "ecs_task" {
  name = "${var.name_prefix}-ecs-task"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

# ECS Task Definition
resource "aws_ecs_task_definition" "main" {
  family                   = var.name_prefix
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.container_cpu
  memory                   = var.container_memory
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name      = var.name_prefix
      image     = "${aws_ecr_repository.main.repository_url}:latest"
      essential = true

      portMappings = [
        {
          containerPort = var.container_port
          hostPort      = var.container_port
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          name  = "FLASK_DEBUG"
          value = "False"
        },
        {
          name  = "FLASK_HOST"
          value = "0.0.0.0"
        },
        {
          name  = "ANTHROPIC_MODEL"
          value = "claude-sonnet-4-20250514"
        },
        {
          name  = "TSR_DB_HOST"
          value = var.db_host
        },
        {
          name  = "TSR_DB_PORT"
          value = tostring(var.db_port)
        },
        {
          name  = "TSR_DB_NAME"
          value = var.db_name
        },
        {
          name  = "TSR_DB_USER"
          value = var.db_username
        },
        {
          name  = "APPLICATION_ROOT"
          value = "/ai-evals"
        }
      ]

      secrets = [
        {
          name      = "ANTHROPIC_API_KEY"
          valueFrom = var.anthropic_api_key_secret_arn
        },
        {
          name      = "TSR_DB_PASSWORD"
          valueFrom = var.db_password_secret_arn
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.main.name
          "awslogs-region"        = data.aws_region.current.name
          "awslogs-stream-prefix" = "ecs"
        }
      }

      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:${var.container_port}/ai-evals/health || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    }
  ])

  tags = {
    Name = "${var.name_prefix}-task"
  }
}

# Get current AWS region
data "aws_region" "current" {}

# Cloud Map Namespace for Service Discovery
resource "aws_service_discovery_private_dns_namespace" "main" {
  name        = "${var.name_prefix}.local"
  description = "Service discovery namespace for ${var.name_prefix}"
  vpc         = var.vpc_id
}

# Cloud Map Service for ECS Service Discovery
resource "aws_service_discovery_service" "main" {
  name = var.name_prefix

  dns_config {
    namespace_id = aws_service_discovery_private_dns_namespace.main.id

    dns_records {
      ttl  = 10
      type = "A"
    }

    routing_policy = "MULTIVALUE"
  }

  health_check_custom_config {
    failure_threshold = 1
  }
}

# ECS Service
resource "aws_ecs_service" "main" {
  name            = var.name_prefix
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.main.arn
  desired_count   = 1

  # Use Fargate Spot with Fargate fallback for capacity availability
  capacity_provider_strategy {
    capacity_provider = "FARGATE_SPOT"
    weight            = 2
    base              = 0
  }

  capacity_provider_strategy {
    capacity_provider = "FARGATE"
    weight            = 1
    base              = 1  # Ensure at least 1 task runs on regular Fargate
  }

  network_configuration {
    subnets          = var.public_subnet_ids
    security_groups  = [var.ecs_security_group_id]
    assign_public_ip = true  # Required for public subnet without NAT
  }

  # Register with ALB target group (if provided)
  dynamic "load_balancer" {
    for_each = var.target_group_arn != "" ? [1] : []
    content {
      target_group_arn = var.target_group_arn
      container_name   = var.name_prefix
      container_port   = var.container_port
    }
  }

  # Service discovery (for API Gateway fallback)
  service_registries {
    registry_arn = aws_service_discovery_service.main.arn
  }

  # Deployment settings
  deployment_maximum_percent         = 200
  deployment_minimum_healthy_percent = 100

  # Ignore task definition changes (managed by CI/CD)
  lifecycle {
    ignore_changes = [task_definition]
  }

  tags = {
    Name = "${var.name_prefix}-service"
  }
}
