output "composer_environment_name" {
  description = "Name of the Cloud Composer environment"
  value       = google_composer_environment.composer_environment.name
}

output "composer_environment_id" {
  description = "ID of the Cloud Composer environment"
  value       = google_composer_environment.composer_environment.id
}

output "composer_gcs_bucket" {
  description = "GCS bucket for Cloud Composer environment"
  value       = google_composer_environment.composer_environment.config[0].dag_gcs_prefix
}

output "composer_airflow_uri" {
  description = "URI of the Airflow web interface"
  value       = google_composer_environment.composer_environment.config[0].airflow_uri
}

output "composer_service_account_email" {
  description = "Email of the service account used by Cloud Composer"
  value       = google_service_account.composer_service_account.email
}

output "composer_dags_gcs_prefix" {
  description = "GCS prefix for DAGs bucket"
  value       = google_composer_environment.composer_environment.config[0].dag_gcs_prefix
}
