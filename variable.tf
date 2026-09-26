variable "redis_node_type" {
  type        = string
  description = "The compute and memory capacity of the cache nodes"
  default     = "cache.t4g.small"
}
