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
