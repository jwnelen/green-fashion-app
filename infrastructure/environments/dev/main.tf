terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "6.8.0"
    }
  }

  backend "gcs" {
    bucket = "green-fashion-terraform-state"
    prefix = "environments/dev"
  }
}

provider "google" {
  project                     = var.project_id
  region                      = var.region
  zone                        = var.zone
  impersonate_service_account = var.impersonate_service_account
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

# Enable required APIs
module "networking" {
  source = "../../modules/networking"

  project_id = var.project_id
}

# GCS Storage
module "gcs" {
  source = "../../modules/gcs"

  service_name                = local.service_name
  environment                 = var.environment
  region                      = var.region
  bucket_versioning_enabled   = var.bucket_versioning_enabled
  bucket_lifecycle_age_days   = var.bucket_lifecycle_age_days
  labels                      = local.labels
}

# IAM
module "iam" {
  source = "../../modules/iam"

  service_name = local.service_name
  environment  = var.environment
  project_id   = var.project_id
  bucket_name  = module.gcs.bucket_name
  labels       = local.labels

  depends_on = [module.gcs]
}

# MongoDB
module "mongodb" {
  source = "../../modules/mongodb"

  service_name = local.service_name
  environment  = var.environment
}

# Auth secrets
module "auth" {
  source = "../../modules/auth"

  service_name = local.service_name
  environment  = var.environment
}

# Cloud Run
module "cloud_run" {
  source = "../../modules/cloud_run"

  service_name                      = local.service_name
  environment                       = var.environment
  region                            = var.region
  project_id                        = var.project_id
  container_image                   = var.container_image
  classifier_api_container_image    = var.classifier_api_container_image
  min_instances                     = var.min_instances
  max_instances                     = var.max_instances
  api_memory                        = var.api_memory
  classifier_memory                 = var.classifier_memory
  api_cpu                           = var.api_cpu
  classifier_cpu                    = var.classifier_cpu
  allowed_ingress                   = var.allowed_ingress
  service_account_email             = module.iam.service_account_email
  bucket_name                       = module.gcs.bucket_name
  mongodb_secret_id                 = module.mongodb.mongodb_secret_id
  google_client_id_secret_id        = module.auth.google_client_id_secret_id
  google_client_secret_id           = module.auth.google_client_secret_id
  labels                            = local.labels

  depends_on = [
    module.networking,
    module.gcs,
    module.iam,
    module.mongodb,
    module.auth
  ]
}
