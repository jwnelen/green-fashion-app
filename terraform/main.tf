terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "6.8.0"
    }
  }

  # Backend configuration for state management
  # Uncomment and configure for production use
  # backend "gcs" {
  #   bucket = "your-terraform-state-bucket"
  #   prefix = "green-fashion"
  # }
}

provider "google" {
  project                     = var.project_id
  region                      = var.region
  zone                        = var.zone
  impersonate_service_account = var.impersonate_service_account
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "run.googleapis.com",
    "cloudbuild.googleapis.com",
    "containerregistry.googleapis.com",
    "storage-api.googleapis.com",
    "secretmanager.googleapis.com",
    "monitoring.googleapis.com",
    "logging.googleapis.com"
  ])

  service = each.value
  project = var.project_id

  disable_on_destroy = false
}

# Local values for resource naming
locals {
  service_name = "green-fashion"
  labels = {
    application = "green-fashion"
    environment = var.environment
    managed-by  = "terraform"
  }
}

resource "google_compute_network" "vpc_network" {
  name = "terraform-network"
}
