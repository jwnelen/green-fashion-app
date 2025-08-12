output "api_url" {
  description = "URL of the deployed API Cloud Run service"
  value       = google_cloud_run_v2_service.green_fashion_api.uri
}

output "api_name" {
  description = "Name of the API Cloud Run service"
  value       = google_cloud_run_v2_service.green_fashion_api.name
}

output "classifier_api_url" {
  description = "URL of the deployed Classifier API Cloud Run service"
  value       = google_cloud_run_v2_service.classifier_api.uri
}

output "classifier_api_name" {
  description = "Name of the Classifier API Cloud Run service"
  value       = google_cloud_run_v2_service.classifier_api.name
}

output "storage_bucket_name" {
  description = "Name of the GCS bucket for images"
  value       = google_storage_bucket.images_bucket.name
}

output "storage_bucket_url" {
  description = "URL of the GCS bucket"
  value       = google_storage_bucket.images_bucket.url
}

output "service_account_email" {
  description = "Email of the service account used by the application"
  value       = google_service_account.app_service_account.email
}

output "project_id" {
  description = "Google Cloud Project ID"
  value       = var.project_id
}

output "region" {
  description = "Google Cloud region"
  value       = var.region
}

output "environment" {
  description = "Environment name"
  value       = var.environment
}

output "mongodb_secret_id" {
  description = "Secret Manager secret ID for MongoDB URI"
  value       = data.google_secret_manager_secret.mongodb_uri.secret_id
}

output "gcs_service_account_key_secret_id" {
  description = "Secret Manager secret ID for GCS service account key"
  value       = var.environment == "dev" ? google_secret_manager_secret.gcs_service_account_key[0].secret_id : null
}
