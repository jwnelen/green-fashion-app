# Cloud Run service for the Streamlit application
resource "google_cloud_run_v2_service" "green_fashion_app" {
  name     = "${local.service_name}-${var.environment}"
  location = var.region

  labels = local.labels

  template {
    labels = local.labels

    # Service account
    service_account = google_service_account.app_service_account.email

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
          cpu    = var.cpu
          memory = var.memory
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
        name  = "GCS_BUCKET_DEV"
        value = "${local.service_name}-dev-images"
      }

      env {
        name  = "GCS_BUCKET_PROD"
        value = "${local.service_name}-prod-images"
      }

      # MongoDB URI from Secret Manager
      env {
        name = "MONGODB_URI"
        value_source {
          secret_key_ref {
            secret  = data.google_secret_manager_secret.mongodb_uri.secret_id
            version = "latest"
          }
        }
      }

      # Ports
      ports {
        container_port = 8080
      }

      # Health check
      startup_probe {
        http_get {
          path = "/_stcore/health"
          port = 8080
        }
        initial_delay_seconds = 60
        timeout_seconds       = 10
        period_seconds        = 10
        failure_threshold     = 3
      }

      liveness_probe {
        http_get {
          path = "/_stcore/health"
          port = 8080
        }
        initial_delay_seconds = 60
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

  depends_on = [
    google_project_service.required_apis,
    google_storage_bucket.images_bucket,
    data.google_secret_manager_secret_version.mongodb_uri
  ]
}

# IAM policy for public access (adjust based on your needs)
resource "google_cloud_run_service_iam_member" "public_access" {
  count = var.allowed_ingress == "all" ? 1 : 0

  location = google_cloud_run_v2_service.green_fashion_app.location
  service  = google_cloud_run_v2_service.green_fashion_app.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Custom domain mapping (optional)
resource "google_cloud_run_domain_mapping" "custom_domain" {
  count = var.custom_domain != "" ? 1 : 0

  location = var.region
  name     = var.custom_domain

  metadata {
    namespace = var.project_id
    labels    = local.labels
  }

  spec {
    route_name = google_cloud_run_v2_service.green_fashion_app.name
  }
}
