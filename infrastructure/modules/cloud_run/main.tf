# Cloud Run service for the API
resource "google_cloud_run_v2_service" "green_fashion_api" {
  name     = "${var.service_name}-${var.environment}"
  location = var.region

  deletion_protection = false

  labels = var.labels

  template {
    labels = var.labels

    # Service account
    service_account = var.service_account_email

    # Scaling configuration
    scaling {
      min_instance_count = var.min_instances
      max_instance_count = var.max_instances
    }

    containers {
      image = var.container_image

      # Resource allocation
      resources {
        limits = {
          cpu    = var.api_cpu
          memory = var.api_memory
        }
        cpu_idle                = true
        startup_cpu_boost       = true
      }

      # Environment variables
      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }

      env {
        name  = "GCS_PROJECT_ID"
        value = var.project_id
      }

      env {
        name  = "GCS_IMAGE_BUCKET"
        value = var.bucket_name
      }

      # MongoDB URI from Secret Manager
      env {
        name = "MONGODB_URI"
        value_source {
          secret_key_ref {
            secret  = var.mongodb_secret_id
            version = "latest"
          }
        }
      }

      env {
        name = "GOOGLE_CLIENT_ID"
        value_source {
          secret_key_ref {
            secret  = var.google_client_id_secret_id
            version = "latest"
          }
        }
      }

      env {
        name = "GOOGLE_CLIENT_SECRET"
        value_source {
          secret_key_ref {
            secret  = var.google_client_secret_id
            version = "latest"
          }
        }
      }

      # MySQL connection string from Secret Manager
      dynamic "env" {
        for_each = var.mysql_connection_secret_id != null ? [1] : []
        content {
          name = "MYSQL_CONNECTION_STRING"
          value_source {
            secret_key_ref {
              secret  = var.mysql_connection_secret_id
              version = "latest"
            }
          }
        }
      }

      # Cloud SQL volume mount
      dynamic "volume_mounts" {
        for_each = var.mysql_instance_connection_name != null ? [1] : []
        content {
          name       = "cloudsql"
          mount_path = "/cloudsql"
        }
      }

      # Cloud SQL environment variables for Unix socket connection
      dynamic "env" {
        for_each = var.mysql_instance_connection_name != null ? [1] : []
        content {
          name  = "INSTANCE_CONNECTION_NAME"
          value = var.mysql_instance_connection_name
        }
      }

      dynamic "env" {
        for_each = var.mysql_db_user != null ? [1] : []
        content {
          name  = "DB_USER"
          value = var.mysql_db_user
        }
      }

      dynamic "env" {
        for_each = var.mysql_db_password != null ? [1] : []
        content {
          name  = "DB_PASS"
          value = var.mysql_db_password
        }
      }

      dynamic "env" {
        for_each = var.mysql_db_name != null ? [1] : []
        content {
          name  = "DB_NAME"
          value = var.mysql_db_name
        }
      }

      # Ports
      ports {
        container_port = 8000
      }

      # Health check
      startup_probe {
        http_get {
          path = "/health"
          port = 8000
        }
        initial_delay_seconds = 30
        timeout_seconds       = 15
        period_seconds        = 15
        failure_threshold     = 5
      }

      liveness_probe {
        http_get {
          path = "/health"
          port = 8000
        }
        initial_delay_seconds = 30
        timeout_seconds       = 10
        period_seconds        = 30
        failure_threshold     = 3
      }
    }

    # Cloud SQL volume
    dynamic "volumes" {
      for_each = var.mysql_instance_connection_name != null ? [1] : []
      content {
        name = "cloudsql"
        cloud_sql_instance {
          instances = [var.mysql_instance_connection_name]
        }
      }
    }

    # Execution environment
    execution_environment = "EXECUTION_ENVIRONMENT_GEN2"
    timeout               = "300s"
  }

  # Traffic configuration
  traffic {
    percent = 100
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }
}

# IAM policy for public access (adjust based on your needs)
resource "google_cloud_run_service_iam_member" "public_access" {
  count = var.allowed_ingress == "all" ? 1 : 0

  location = google_cloud_run_v2_service.green_fashion_api.location
  service  = google_cloud_run_v2_service.green_fashion_api.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Cloud Run service for the Classifier API
resource "google_cloud_run_v2_service" "classifier_api" {
  name     = "classifier-api-${var.environment}"
  location = var.region

  deletion_protection = false

  labels = var.labels

  template {
    labels = var.labels

    # Service account
    service_account = var.service_account_email

    # Scaling configuration
    scaling {
      min_instance_count = var.min_instances
      max_instance_count = var.max_instances
    }

    containers {
      image = var.classifier_api_container_image

      # Resource allocation
      resources {
        limits = {
          cpu    = var.classifier_cpu
          memory = var.classifier_memory
        }
        cpu_idle                = true
        startup_cpu_boost       = true
      }

      # Environment variables
      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }

      env {
        name  = "GCS_PROJECT_ID"
        value = var.project_id
      }

      env {
        name  = "GCS_IMAGE_BUCKET"
        value = var.bucket_name
      }

      # Ports
      ports {
        container_port = 8001
      }

      # Health check
      startup_probe {
        http_get {
          path = "/health"
          port = 8001
        }
        initial_delay_seconds = 60
        timeout_seconds       = 30
        period_seconds        = 30
        failure_threshold     = 5
      }

      liveness_probe {
        http_get {
          path = "/health"
          port = 8001
        }
        initial_delay_seconds = 30
        timeout_seconds       = 10
        period_seconds        = 30
        failure_threshold     = 3
      }
    }

    # Execution environment
    execution_environment = "EXECUTION_ENVIRONMENT_GEN2"
    timeout               = "300s"
  }

  # Traffic configuration
  traffic {
    percent = 100
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }
}

# IAM policy for classifier API public access
resource "google_cloud_run_service_iam_member" "classifier_api_public_access" {
  count = var.allowed_ingress == "all" ? 1 : 0

  location = google_cloud_run_v2_service.classifier_api.location
  service  = google_cloud_run_v2_service.classifier_api.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
