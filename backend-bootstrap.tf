# 1. Random Suffix for Unique S3 Bucket Name
resource "random_id" "bucket_suffix" {
  byte_length = 4
}

# 2. KMS Key for Encrypting Terraform State Files
resource "aws_kms_key" "tf_state_key" {
  description             = "KMS key for Terraform state storage encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true

  tags = {
    Name      = "terraform-state-kms-key"
    ManagedBy = "Terraform"
  }
}

resource "aws_kms_alias" "tf_state_key_alias" {
  name          = "alias/terraform-state-key"
  target_key_id = aws_kms_key.tf_state_key.key_id
}

# 3. S3 Bucket for Storing State Files
resource "aws_s3_bucket" "terraform_state" {
  bucket        = "smarthospital-tfstate-${random_id.bucket_suffix.hex}"
  force_destroy = false # Prevent accidental deletion of state bucket

  lifecycle {
    prevent_destroy = true
  }

  tags = {
    Name      = "Terraform State Storage"
    ManagedBy = "Terraform"
  }
}

# Enable S3 Bucket Versioning (Crucial for state file recovery)
resource "aws_s3_bucket_versioning" "terraform_state_versioning" {
  bucket = aws_s3_bucket.terraform_state.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Enable Server-Side Encryption (SSE-KMS)
resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state_crypto" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.tf_state_key.arn
      sse_algorithm     = "aws:kms"
    }
  }
}

# Block Public Access to State Bucket
resource "aws_s3_bucket_public_access_block" "terraform_state_public_block" {
  bucket                  = aws_s3_bucket.terraform_state.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# 4. DynamoDB Table for State Locking
resource "aws_dynamodb_table" "terraform_locks" {
  name         = "smarthospital-tf-state-locks"
  billing_mode = "PAY_PER_REQUEST" # Serverless on-demand pricing
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }

  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.tf_state_key.arn
  }

  tags = {
    Name      = "Terraform State Lock Table"
    ManagedBy = "Terraform"
  }
}

# 5. Outputs for configuring backend block
output "s3_bucket_name" {
  description = "Name of the created S3 state bucket"
  value       = aws_s3_bucket.terraform_state.bucket
}

output "dynamodb_table_name" {
  description = "Name of the DynamoDB lock table"
  value       = aws_dynamodb_table.terraform_locks.name
}

output "backend_config_snippet" {
  description = "Copy-pasteable backend configuration snippet"
  value       = <<EOF
terraform {
  backend "s3" {
    bucket         = "${aws_s3_bucket.terraform_state.bucket}"
    key            = "global/s3/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "${aws_dynamodb_table.terraform_locks.name}"
    encrypt        = true
    kms_key_id     = "${aws_kms_key.tf_state_key.arn}"
  }
}
EOF
}
