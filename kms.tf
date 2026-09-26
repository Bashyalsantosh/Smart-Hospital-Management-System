resource "aws_kms_key" "hospital_kms" {
  description             = "KMS Key for Smart Hospital PHI Encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true

  tags = {
    Name = "${var.environment}-hospital-kms-key"
  }
}

resource "aws_kms_alias" "hospital_kms_alias" {
  name          = "alias/${var.environment}-smart-hospital"
  target_key_id = aws_kms_key.hospital_kms.key_id
}
