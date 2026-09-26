variable "aws_region" {
  type        = string
  default     = "us-east-1"
  description = "AWS region for Smart Hospital resources"
}

variable "environment" {
  type        = string
  default     = "prod"
  description = "Environment name (e.g., dev, staging, prod)"
}

variable "vpc_cidr" {
  type        = string
  default     = "10.0.0.0/16"
  description = "VPC CIDR block"
}

variable "db_name" {
  type        = string
  default     = "smarthospital"
  description = "Aurora PostgreSQL database name"
}

variable "db_master_username" {
  type        = string
  default     = "hospital_admin"
  description = "Master username for Aurora DB"
}

variable "container_image" {
  type        = string
  default     = "123456789012.dkr.ecr.us-east-1.amazonaws.com/hmis-backend:v1.0"
  description = "ECR Image URI for backend HMIS service"
}
