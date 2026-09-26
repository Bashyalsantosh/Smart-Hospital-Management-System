output "redis_primary_endpoint" {
  description = "Redis primary endpoint address for write operations"
  value       = aws_elasticache_replication_group.redis.primary_endpoint_address
  sensitive   = true
}

output "redis_reader_endpoint" {
  description = "Redis reader endpoint address for read-only query caching"
  value       = aws_elasticache_replication_group.redis.reader_endpoint_address
  sensitive   = true
}
