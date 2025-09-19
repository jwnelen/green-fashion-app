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
    prefix = "environments/prod"
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

  service_name              = local.service_name
  environment               = var.environment
  region                    = var.region
  bucket_versioning_enabled = var.bucket_versioning_enabled
  bucket_lifecycle_age_days = var.bucket_lifecycle_age_days
  labels                    = local.labels
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

# MySQL (optional)
module "mysql" {
  count  = var.mysql_enabled ? 1 : 0
  source = "../../modules/mysql"

  service_name        = local.service_name
  environment         = var.environment
  region              = var.region
  db_tier             = var.mysql_db_tier
  db_disk_size        = var.mysql_db_disk_size
  high_availability   = var.mysql_high_availability
  db_password         = var.mysql_db_password
  deletion_protection = var.mysql_deletion_protection
  labels              = local.labels
}

# Cloud Composer (optional)
module "composer" {
  count  = var.composer_enabled ? 1 : 0
  source = "../../modules/composer"

  service_name            = local.service_name
  environment             = var.environment
  region                  = var.region
  project_id              = var.project_id
  zone                    = var.zone
  airflow_image_version   = var.composer_airflow_image_version
  machine_type            = var.composer_machine_type
  disk_size_gb            = var.composer_disk_size_gb
  database_machine_type   = var.composer_database_machine_type
  web_server_machine_type = var.composer_web_server_machine_type
  scheduler_cpu           = var.composer_scheduler_cpu
  scheduler_memory_gb     = var.composer_scheduler_memory_gb
  worker_min_count        = var.composer_worker_min_count
  worker_max_count        = var.composer_worker_max_count
  airflow_env_variables   = var.composer_airflow_env_variables
  pypi_packages          = var.composer_pypi_packages
  labels                 = local.labels

  depends_on = [
    module.networking
  ]
}

# Cloud Run
module "cloud_run" {
  source = "../../modules/cloud_run"

  service_name                   = local.service_name
  environment                    = var.environment
  region                         = var.region
  project_id                     = var.project_id
  container_image                = var.container_image
  classifier_api_container_image = var.classifier_api_container_image
  min_instances                  = var.min_instances
  max_instances                  = var.max_instances
  api_memory                     = var.api_memory
  classifier_memory              = var.classifier_memory
  api_cpu                        = var.api_cpu
  classifier_cpu                 = var.classifier_cpu
  allowed_ingress                = var.allowed_ingress
  service_account_email          = module.iam.service_account_email
  bucket_name                    = module.gcs.bucket_name
  mongodb_secret_id              = module.mongodb.mongodb_secret_id
  google_client_id_secret_id     = module.auth.google_client_id_secret_id
  google_client_secret_id        = module.auth.google_client_secret_id
  mysql_connection_secret_id     = var.mysql_enabled ? module.mysql[0].mysql_connection_secret_id : null
  mysql_instance_connection_name = var.mysql_enabled ? module.mysql[0].mysql_instance_connection_name : null
  mysql_db_user                  = var.mysql_enabled ? "${local.service_name}_user" : null
  mysql_db_password              = var.mysql_enabled ? var.mysql_db_password : null
  mysql_db_name                  = var.mysql_enabled ? "${local.service_name}_${var.environment}" : null
  labels                         = local.labels

  depends_on = [
    module.networking,
    module.gcs,
    module.iam,
    module.mongodb,
    module.mysql,
    module.auth
  ]
}
