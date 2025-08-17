resource "google_secret_manager_secret" "google_client_id" {
    secret_id = "${var.service_name}-google-client-id-${var.environment}"

    replication {
      auto {}
    }
  }

  # Google Client Secret (sensitive, must be in Secret Manager)
  resource "google_secret_manager_secret" "google_client_secret" {
    secret_id = "${var.service_name}-google-client-secret-${var.environment}"

    replication {
      auto {}
    }
  }
