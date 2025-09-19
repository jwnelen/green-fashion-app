variable "project_id" {
  description = "Google Cloud Project ID"
  type        = string
}

variable "impersonate_service_account" {
  description = "Service account to impersonate for Terraform operations"
  type        = string
  default     = null
}

variable "region" {
  description = "Google Cloud region"
  type        = string
  default     = "europe-west4"
}

variable "zone" {
  description = "Google Cloud zone"
  type        = string
  default     = "europe-west4-a"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "container_image" {
  description = "Container image URL for Cloud Run"
  type        = string
  default     = "gcr.io/PROJECT_ID/green-fashion:latest"
}

variable "classifier_api_container_image" {
  description = "Container image URL for Classifier API Cloud Run"
  type        = string
  default     = "gcr.io/PROJECT_ID/classifier-api:latest"
}

variable "min_instances" {
  description = "Minimum number of Cloud Run instances"
  type        = number
  default     = 0
}

variable "max_instances" {
  description = "Maximum number of Cloud Run instances"
  type        = number
  default     = 10
}

variable "api_memory" {
  description = "Memory allocation for API Cloud Run service"
  type        = string
  default     = "1Gi"
}

variable "classifier_memory" {
  description = "Memory allocation for Classifier API Cloud Run service"
  type        = string
  default     = "2Gi"
}

variable "api_cpu" {
  description = "CPU allocation for API Cloud Run service"
  type        = string
  default     = "1"
}

variable "classifier_cpu" {
  description = "CPU allocation for Classifier API Cloud Run service"
  type        = string
  default     = "2"
}

variable "allowed_ingress" {
  description = "Allowed ingress for Cloud Run service"
  type        = string
  default     = "all"
  validation {
    condition     = contains(["all", "internal", "internal-and-cloud-load-balancing"], var.allowed_ingress)
    error_message = "Allowed ingress must be all, internal, or internal-and-cloud-load-balancing."
  }
}

variable "custom_domain" {
  description = "Custom domain for the service (optional)"
  type        = string
  default     = ""
}

variable "enable_cdn" {
  description = "Enable Cloud CDN for static assets"
  type        = bool
  default     = false
}

variable "bucket_versioning_enabled" {
  description = "Enable versioning on storage buckets"
  type        = bool
  default     = false
}

variable "bucket_lifecycle_age_days" {
  description = "Age in days for bucket lifecycle deletion"
  type        = number
  default     = 365
}

variable "mysql_enabled" {
  description = "Enable MySQL Cloud SQL database"
  type        = bool
  default     = false
}

variable "mysql_db_tier" {
  description = "Cloud SQL tier for MySQL instance"
  type        = string
  default     = "db-standard-1"
}

variable "mysql_db_disk_size" {
  description = "MySQL database disk size in GB"
  type        = number
  default     = 10
}

variable "mysql_high_availability" {
  description = "Enable high availability for MySQL"
  type        = bool
  default     = false
}

variable "mysql_db_password" {
  description = "MySQL database password"
  type        = string
  sensitive   = true
  default     = null
}

variable "mysql_deletion_protection" {
  description = "Enable deletion protection for MySQL"
  type        = bool
  default     = true
}

# Cloud Composer variables
variable "composer_enabled" {
  description = "Enable Cloud Composer environment"
  type        = bool
  default     = false
}

variable "composer_airflow_image_version" {
  description = "Airflow image version for Cloud Composer"
  type        = string
  default     = "composer-3-airflow-2.10.5-build.14"
}

variable "composer_machine_type" {
  description = "Machine type for Composer nodes"
  type        = string
  default     = "n1-standard-1"
}

variable "composer_disk_size_gb" {
  description = "Disk size in GB for Composer nodes"
  type        = number
  default     = 100
}

variable "composer_database_machine_type" {
  description = "Machine type for the Composer database"
  type        = string
  default     = "db-n1-standard-2"
}

variable "composer_web_server_machine_type" {
  description = "Machine type for the Composer web server"
  type        = string
  default     = "composer-n1-webserver-2"
}


variable "composer_scheduler_cpu" {
  description = "CPU allocation for Composer scheduler"
  type        = number
  default     = 0.5
}

variable "composer_scheduler_memory_gb" {
  description = "Memory allocation for Composer scheduler in GB"
  type        = number
  default     = 1.875
}

variable "composer_worker_min_count" {
  description = "Minimum number of Composer workers"
  type        = number
  default     = 1
}

variable "composer_worker_max_count" {
  description = "Maximum number of Composer workers"
  type        = number
  default     = 3
}

variable "composer_airflow_env_variables" {
  description = "Environment variables for Airflow in Composer"
  type        = map(string)
  default     = {}
}

variable "composer_pypi_packages" {
  description = "PyPI packages to install in the Composer environment"
  type        = map(string)
  default     = {}
}
