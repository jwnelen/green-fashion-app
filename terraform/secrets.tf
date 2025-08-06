# Secret Manager for sensitive configuration
resource "google_secret_manager_secret" "mongodb_uri" {
  secret_id = "${local.service_name}-${var.environment}-mongodb-uri"

  labels = local.labels

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "mongodb_uri" {
  secret      = google_secret_manager_secret.mongodb_uri.id
  secret_data = var.mongodb_uri
}

# Service account key for GCS access (optional - using workload identity is preferred)
resource "google_service_account_key" "app_key" {
  count              = var.environment == "dev" ? 1 : 0
  service_account_id = google_service_account.app_service_account.name
  public_key_type    = "TYPE_X509_PEM_FILE"
}

resource "google_secret_manager_secret" "gcs_service_account_key" {
  count     = var.environment == "dev" ? 1 : 0
  secret_id = "${local.service_name}-${var.environment}-gcs-key"

  labels = local.labels

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "gcs_service_account_key" {
  count       = var.environment == "dev" ? 1 : 0
  secret      = google_secret_manager_secret.gcs_service_account_key[0].id
  secret_data = base64decode(google_service_account_key.app_key[0].private_key)
}
