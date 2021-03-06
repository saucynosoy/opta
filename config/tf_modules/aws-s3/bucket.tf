resource "aws_s3_bucket" "bucket" {
  bucket = var.bucket_name
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
  force_destroy = true

  versioning {
    enabled = true
  }

  logging {
    target_bucket = var.s3_log_bucket_name
    target_prefix = "log/"
  }

  lifecycle_rule {
    enabled = true

    noncurrent_version_transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    noncurrent_version_transition {
      days          = 60
      storage_class = "GLACIER"
    }

    noncurrent_version_expiration {
      days = 90
    }
  }

  dynamic "cors_rule" {
    for_each = var.cors_rule != null ? [var.cors_rule] : []
    content {
      allowed_headers = try(cors_rule.value["allowed_headers"], [])
      allowed_methods = try(cors_rule.value["allowed_methods"], [])
      allowed_origins = try(cors_rule.value["allowed_origins"], [])
      expose_headers  = try(cors_rule.value["expose_headers"], [])
      max_age_seconds = try(cors_rule.value["max_age_seconds"], 0)
    }
  }

  dynamic "replication_configuration" {
    for_each = var.same_region_replication ? [1] : []
    content {
      role = aws_iam_role.replication[0].arn
      rules {
        id     = "default"
        status = "Enabled"

        destination {
          bucket        = aws_s3_bucket.replica[0].arn
          storage_class = "STANDARD"
        }
      }
    }
  }
}

resource "aws_s3_bucket_public_access_block" "block" {
  count  = var.block_public ? 1 : 0
  bucket = aws_s3_bucket.bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_policy" "policy" {
  count  = var.bucket_policy == null ? 0 : 1
  bucket = aws_s3_bucket.bucket.id
  policy = var.bucket_policy == null ? null : jsonencode(var.bucket_policy)
}
