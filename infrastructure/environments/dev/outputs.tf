output "api_url" {
  description = "URL of the deployed API Cloud Run service"
  value       = module.cloud_run.api_url
}

output "api_name" {
  description = "Name of the API Cloud Run service"
  value       = module.cloud_run.api_name
}

output "classifier_api_url" {
  description = "URL of the deployed Classifier API Cloud Run service"
  value       = module.cloud_run.classifier_api_url
}

output "classifier_api_name" {
  description = "Name of the Classifier API Cloud Run service"
  value       = module.cloud_run.classifier_api_name
}

output "storage_bucket_name" {
  description = "Name of the GCS bucket for images"
  value       = module.gcs.bucket_name
}

output "storage_bucket_url" {
  description = "URL of the GCS bucket"
  value       = module.gcs.bucket_url
}

output "service_account_email" {
  description = "Email of the service account used by the application"
  value       = module.iam.service_account_email
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
  value       = module.mongodb.mongodb_secret_id
}

output "gcs_service_account_key_secret_id" {
  description = "Secret Manager secret ID for GCS service account key"
  value       = module.iam.gcs_service_account_key_secret_id
}

# Cloud Composer outputs (conditional)
output "composer_environment_name" {
  description = "Name of the Cloud Composer environment"
  value       = var.composer_enabled ? module.composer[0].composer_environment_name : null
}

output "composer_airflow_uri" {
  description = "URI of the Airflow web interface"
  value       = var.composer_enabled ? module.composer[0].composer_airflow_uri : null
}

output "composer_gcs_bucket" {
  description = "GCS bucket for Cloud Composer environment"
  value       = var.composer_enabled ? module.composer[0].composer_gcs_bucket : null
}

output "composer_service_account_email" {
  description = "Email of the service account used by Cloud Composer"
  value       = var.composer_enabled ? module.composer[0].composer_service_account_email : null
}
