# Service account for application
resource "google_service_account" "app_service_account" {
  account_id   = "${var.service_name}-${var.environment}"
  display_name = "Green Fashion App Service Account (${var.environment})"
  description  = "Service account for Green Fashion application in ${var.environment}"
}

# IAM binding for storage access
resource "google_storage_bucket_iam_member" "app_storage_admin" {
  bucket = var.bucket_name
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

# Service account key for GCS access (optional - using workload identity is preferred)
resource "google_service_account_key" "app_key" {
  count              = var.environment == "dev" ? 1 : 0
  service_account_id = google_service_account.app_service_account.name
  public_key_type    = "TYPE_X509_PEM_FILE"
}

resource "google_secret_manager_secret" "gcs_service_account_key" {
  count     = var.environment == "dev" ? 1 : 0
  secret_id = "${var.service_name}-${var.environment}-gcs-key"

  labels = var.labels

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "gcs_service_account_key" {
  count       = var.environment == "dev" ? 1 : 0
  secret      = google_secret_manager_secret.gcs_service_account_key[0].id
  secret_data = base64decode(google_service_account_key.app_key[0].private_key)
}
