# ------------------------------------------------------------------------------
# ElastiCache Subnet Group (Private Subnets)
# ------------------------------------------------------------------------------
resource "aws_elasticache_subnet_group" "redis" {
  name       = "hmis-redis-subnet-group-${var.environment}"
  subnet_ids = aws_subnet.private[*].id  # Assumes private subnets defined in vpc.tf

  tags = {
    Name        = "hmis-redis-subnet-group"
    Environment = var.environment
  }
}

# ------------------------------------------------------------------------------
# ElastiCache Security Group
# ------------------------------------------------------------------------------
resource "aws_security_group" "redis" {
  name        = "hmis-redis-sg-${var.environment}"
  description = "Security group for ElastiCache Redis cluster restricting access to ECS Fargate tasks"
  vpc_id      = aws_vpc.main.id

  # Allow inbound Redis traffic exclusively from ECS tasks security group
  ingress {
    description     = "Redis port from ECS backend tasks"
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_tasks.id]
  }

  egress {
    description = "Allow all outbound traffic for cluster maintenance"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "hmis-redis-sg"
    Environment = var.environment
  }
}

# ------------------------------------------------------------------------------
# Generate Secure Redis AUTH Token
# ------------------------------------------------------------------------------
resource "random_password" "redis_auth_token" {
  length  = 64
  special = false
}

# Store Auth Token in AWS Systems Manager Parameter Store (Encrypted with KMS)
resource "aws_ssm_parameter" "redis_auth_token" {
  name        = "/hmis/${var.environment}/redis/auth_token"
  description = "Auth token for Redis cluster authentication"
  type        = "SecureString"
  value       = random_password.redis_auth_token.result
  key_id      = aws_kms_key.hospital_key.arn # References KMS key from kms.tf

  tags = {
    Environment = var.environment
  }
}

# ------------------------------------------------------------------------------
# ElastiCache Parameter Group (Redis 7.x)
# ------------------------------------------------------------------------------
resource "aws_elasticache_parameter_group" "redis" {
  name   = "hmis-redis7-params-${var.environment}"
  family = "redis7"

  parameter {
    name  = "maxmemory-policy"
    value = "volatile-lru" # Evict least recently used keys with TTL when memory is full
  }
}

# ------------------------------------------------------------------------------
# ElastiCache Replication Group (Redis Cluster with Encryption & Replication)
# ------------------------------------------------------------------------------
resource "aws_elasticache_replication_group" "redis" {
  replication_group_id          = "hmis-redis-cluster-${var.environment}"
  description                   = "Secure multi-tenant Redis cluster for HMIS caching"
  node_type                     = var.redis_node_type
  port                          = 6379
  parameter_group_name          = aws_elasticache_parameter_group.redis.name
  subnet_group_name             = aws_elasticache_subnet_group.redis.name
  security_group_ids            = [aws_security_group.redis.id]

  # High Availability & Replication
  num_cache_clusters            = 2 # Primary + 1 Read Replica
  automatic_failover_enabled    = true
  multi_az_enabled              = true

  # Security & Encryption
  at_rest_encryption_enabled    = true
  kms_key_id                    = aws_kms_key.hospital_key.arn
  transit_encryption_enabled    = true
  auth_token                    = random_password.redis_auth_token.result

  # Maintenance & Backups
  snapshot_window               = "03:00-05:00"
  snapshot_retention_limit      = 7
  auto_minor_version_upgrade    = true

  tags = {
    Name        = "hmis-redis-cluster"
    Environment = var.environment
  }
}
