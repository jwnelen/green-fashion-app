# Enable required APIs
resource "google_project_service" "composer_api" {
  project = var.project_id
  service = "composer.googleapis.com"

  # Disabling Cloud Composer API might irreversibly break all other
  # environments in your project.
  disable_on_destroy = false
}

# Service account for Cloud Composer
resource "google_service_account" "composer_service_account" {
  account_id   = "${var.service_name}-composer-${var.environment}"
  display_name = "Cloud Composer Service Account - ${var.environment}"
  project      = var.project_id
}

# IAM role for the service account
resource "google_project_iam_member" "composer_worker" {
  project = var.project_id
  member  = "serviceAccount:${google_service_account.composer_service_account.email}"
  role    = "roles/composer.worker"
}

# Additional IAM roles needed for Cloud Composer
resource "google_project_iam_member" "composer_storage_admin" {
  project = var.project_id
  member  = "serviceAccount:${google_service_account.composer_service_account.email}"
  role    = "roles/storage.admin"
}

resource "google_project_iam_member" "composer_bigquery_user" {
  project = var.project_id
  member  = "serviceAccount:${google_service_account.composer_service_account.email}"
  role    = "roles/bigquery.user"
}

# Cloud Composer Environment
resource "google_composer_environment" "composer_environment" {
  name     = "${var.service_name}-composer-${var.environment}"
  region   = var.region
  project  = var.project_id

  labels = var.labels

  config {
    software_config {
      image_version = var.airflow_image_version

      # Environment variables for Airflow
      env_variables = var.airflow_env_variables

      # PyPI packages
      pypi_packages = var.pypi_packages
    }

    # Remove node_config, database_config, and web_server_config
    # These are not supported in Composer 3.x
    # Use workloads_config instead

    # Workloads configuration - only supported config for Composer 3.x
    workloads_config {
      scheduler {
        cpu        = var.scheduler_cpu
        memory_gb  = var.scheduler_memory_gb
        storage_gb = var.scheduler_storage_gb
        count      = var.scheduler_count
      }

      web_server {
        cpu        = var.web_server_cpu
        memory_gb  = var.web_server_memory_gb
        storage_gb = var.web_server_storage_gb
      }

      worker {
        cpu        = var.worker_cpu
        memory_gb  = var.worker_memory_gb
        storage_gb = var.worker_storage_gb
        min_count  = var.worker_min_count
        max_count  = var.worker_max_count
      }
    }
  }

  depends_on = [
    google_project_service.composer_api,
    google_service_account.composer_service_account,
    google_project_iam_member.composer_worker,
    google_project_iam_member.composer_storage_admin,
    google_project_iam_member.composer_bigquery_user
  ]
}
