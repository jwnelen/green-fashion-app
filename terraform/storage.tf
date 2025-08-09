# Google Cloud Storage buckets for image storage
resource "google_storage_bucket" "images_bucket" {
  name          = "${local.service_name}-${var.environment}-images"
  location      = var.region
  force_destroy = var.environment == "dev" ? true : false

  labels = local.labels

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

  # Note: For production, manually set prevent_destroy = true in lifecycle block
}

# Service account for application
resource "google_service_account" "app_service_account" {
  account_id   = "${local.service_name}-${var.environment}"
  display_name = "Green Fashion App Service Account (${var.environment})"
  description  = "Service account for Green Fashion application in ${var.environment}"
}

# IAM binding for storage access
resource "google_storage_bucket_iam_member" "app_storage_admin" {
  bucket = google_storage_bucket.images_bucket.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.app_service_account.email}"
}

# Additional IAM roles for the service account
resource "google_project_iam_member" "app_service_account_roles" {
  for_each = toset([
    "roles/secretmanager.secretAccessor",
    "roles/logging.logWriter",
    "roles/monitoring.metricWriter",
  ])

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.app_service_account.email}"
}
