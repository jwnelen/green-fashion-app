# Google Cloud Storage buckets for image storage
resource "google_storage_bucket" "images_bucket" {
  name          = "${var.service_name}-${var.environment}-images"
  location      = var.region
  force_destroy = var.environment == "dev" ? true : false

  labels = var.labels

  # Versioning
  versioning {
    enabled = var.bucket_versioning_enabled
  }

  # Lifecycle management
  lifecycle_rule {
    condition {
      age = var.bucket_lifecycle_age_days
    }
    action {
      type = "Delete"
    }
  }

  # CORS configuration for web access
  cors {
    origin          = ["*"]
    method          = ["GET", "HEAD", "PUT", "POST", "DELETE"]
    response_header = ["*"]
    max_age_seconds = 3600
  }

  # Uniform bucket-level access
  uniform_bucket_level_access = true
}
