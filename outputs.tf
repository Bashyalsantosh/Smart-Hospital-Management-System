output "vpc_id" {
  description = "The ID of the Smart Hospital VPC"
  value       = aws_vpc.hospital_vpc.id
}

output "aurora_endpoint" {
  description = "Aurora PostgreSQL Primary Endpoint"
  value       = aws_rds_cluster.aurora_cluster.endpoint
}

output "s3_bucket_name" {
  description = "HIPAA PHI Storage S3 Bucket"
  value       = aws_s3_bucket.phi_storage.bucket
}

output "ecs_cluster_name" {
  description = "Name of the ECS Cluster running backend APIs"
  value       = aws_ecs_cluster.hospital_cluster.name
}
