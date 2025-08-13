output "service_account_email" {
  description = "Email of the service account used by the application"
  value       = google_service_account.app_service_account.email
}

output "gcs_service_account_key_secret_id" {
  description = "Secret Manager secret ID for GCS service account key"
  value       = var.environment == "dev" ? google_secret_manager_secret.gcs_service_account_key[0].secret_id : null
}
