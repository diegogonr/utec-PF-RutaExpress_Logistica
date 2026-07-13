terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.60"
    }
  }
}

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

locals {
  mobile_api_image = var.mobile_api_image != "" ? var.mobile_api_image : "${aws_ecr_repository.mobile_api.repository_url}:latest"
}

resource "aws_ecr_repository" "mobile_api" {
  name                 = "${var.prefix}-mobile-api"
  image_tag_mutability = "MUTABLE"
  force_delete         = true
  tags                 = var.tags

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_kms_key" "evidence" {
  description             = "RutaExpress MVP evidence encryption"
  deletion_window_in_days = 7
  enable_key_rotation     = true
  tags                    = var.tags
}

resource "aws_kms_alias" "evidence" {
  name          = "alias/${var.prefix}-evidence"
  target_key_id = aws_kms_key.evidence.key_id
}

resource "aws_s3_bucket" "evidence" {
  bucket = var.s3_evidence_bucket
  tags   = var.tags
}

resource "aws_s3_bucket_server_side_encryption_configuration" "evidence" {
  bucket = aws_s3_bucket.evidence.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.evidence.arn
    }
  }
}

resource "aws_s3_bucket_public_access_block" "evidence" {
  bucket                  = aws_s3_bucket.evidence.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "evidence" {
  bucket = aws_s3_bucket.evidence.id
  rule {
    id     = "expire-90d"
    status = "Enabled"
    filter {
      prefix = ""
    }
    expiration {
      days = 90
    }
  }
}

resource "aws_dynamodb_table" "mobile_outbox" {
  name         = var.dynamodb_table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "pk"
  range_key    = "sk"
  tags         = var.tags

  attribute {
    name = "pk"
    type = "S"
  }
  attribute {
    name = "sk"
    type = "S"
  }
  attribute {
    name = "status"
    type = "S"
  }

  global_secondary_index {
    name            = "gsi-status"
    hash_key        = "status"
    range_key       = "sk"
    projection_type = "ALL"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }
}

resource "aws_sqs_queue" "mobile_dlq" {
  name                      = var.sqs_dlq_name
  message_retention_seconds = 1209600
  tags                      = var.tags
}

resource "aws_sqs_queue" "mobile_bridge" {
  name                       = var.sqs_mobile_queue
  visibility_timeout_seconds = 60
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.mobile_dlq.arn
    maxReceiveCount     = 5
  })
  tags = var.tags
}

resource "aws_cloudwatch_event_bus" "bridge" {
  name = "${var.prefix}-bridge"
  tags = var.tags
}

resource "aws_cloudwatch_event_rule" "to_azure_placeholder" {
  name           = "${var.prefix}-mobile-to-hub"
  description    = "Reenvía eventos móviles hacia Azure Event Hubs (configurar target con connection string en Key Vault)"
  event_bus_name = aws_cloudwatch_event_bus.bridge.name
  event_pattern = jsonencode({
    source = ["rutaexpress.mobile"]
  })
  tags = var.tags
}

resource "aws_iam_role" "ecs_task_execution" {
  name = "${var.prefix}-ecs-exec"
  tags = var.tags

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "ecs_task" {
  name = "${var.prefix}-ecs-task"
  tags = var.tags

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy" "ecs_task" {
  name = "${var.prefix}-ecs-task-policy"
  role = aws_iam_role.ecs_task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem", "dynamodb:PutItem", "dynamodb:UpdateItem", "dynamodb:Query",
          "s3:PutObject", "s3:GetObject",
          "sqs:ReceiveMessage", "sqs:DeleteMessage", "sqs:GetQueueAttributes", "sqs:SendMessage",
          "events:PutEvents",
          "kms:Encrypt", "kms:Decrypt", "kms:GenerateDataKey"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_ecs_cluster" "main" {
  name = var.ecs_cluster_name
  tags = var.tags

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

resource "aws_cloudwatch_log_group" "mobile_api" {
  name              = "/ecs/${var.prefix}-mobile-api"
  retention_in_days = 14
  tags              = var.tags
}

resource "aws_ecs_task_definition" "mobile_api" {
  family                   = "${var.prefix}-mobile-api"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn
  tags                     = var.tags

  container_definitions = jsonencode([
    {
      name      = "mobile-api"
      image     = local.mobile_api_image
      essential = true
      portMappings = [{ containerPort = 8080, protocol = "tcp" }]
      environment = [
        { name = "DYNAMODB_TABLE", value = aws_dynamodb_table.mobile_outbox.name },
        { name = "S3_BUCKET", value = aws_s3_bucket.evidence.bucket },
        { name = "SQS_QUEUE_URL", value = aws_sqs_queue.mobile_bridge.url },
        { name = "EVENT_BUS_NAME", value = aws_cloudwatch_event_bus.bridge.name },
        { name = "AWS_REGION", value = data.aws_region.current.name }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.mobile_api.name
          awslogs-region        = data.aws_region.current.name
          awslogs-stream-prefix = "mobile"
        }
      }
    },
    {
      name      = "retry-worker"
      image     = local.mobile_api_image
      essential = true
      command   = ["node", "src/retry-worker.js"]
      environment = [
        { name = "SQS_QUEUE_URL", value = aws_sqs_queue.mobile_bridge.url },
        { name = "EVENT_BUS_NAME", value = aws_cloudwatch_event_bus.bridge.name },
        { name = "JITTER_MS", value = "500" }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.mobile_api.name
          awslogs-region        = data.aws_region.current.name
          awslogs-stream-prefix = "retry"
        }
      }
    }
  ])
}

resource "aws_default_vpc" "default" {}

resource "aws_default_subnet" "a" {
  availability_zone = "${data.aws_region.current.name}a"
}

resource "aws_default_subnet" "b" {
  availability_zone = "${data.aws_region.current.name}b"
}

resource "aws_security_group" "alb" {
  name        = "${var.prefix}-alb-sg"
  description = "ALB mobile API port 80 from Internet"
  vpc_id      = aws_default_vpc.default.id
  tags        = var.tags

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "ecs" {
  name        = "${var.prefix}-ecs-sg"
  description = "ECS Fargate mobile API"
  vpc_id      = aws_default_vpc.default.id
  tags        = var.tags

  ingress {
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_lb" "mobile" {
  name               = "${var.prefix}-mobile-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = [aws_default_subnet.a.id, aws_default_subnet.b.id]
  tags               = var.tags
}

resource "aws_lb_target_group" "mobile" {
  name        = "${var.prefix}-mobile-tg"
  port        = 8080
  protocol    = "HTTP"
  vpc_id      = aws_default_vpc.default.id
  target_type = "ip"
  tags        = var.tags

  health_check {
    path = "/health"
  }
}

resource "aws_lb_listener" "mobile" {
  load_balancer_arn = aws_lb.mobile.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.mobile.arn
  }
}

resource "aws_ecs_service" "mobile_api" {
  name            = "${var.prefix}-mobile-api"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.mobile_api.arn
  desired_count   = 1
  launch_type     = "FARGATE"
  tags            = var.tags

  network_configuration {
    subnets          = [aws_default_subnet.a.id, aws_default_subnet.b.id]
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.mobile.arn
    container_name   = "mobile-api"
    container_port   = 8080
  }

  depends_on = [aws_lb_listener.mobile]
}
