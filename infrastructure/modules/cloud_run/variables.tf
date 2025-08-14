variable "service_name" {
  description = "Base name for the service"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "region" {
  description = "Google Cloud region"
  type        = string
}

variable "project_id" {
  description = "Google Cloud Project ID"
  type        = string
}

variable "container_image" {
  description = "Container image URL for Cloud Run"
  type        = string
}

variable "classifier_api_container_image" {
  description = "Container image URL for Classifier API Cloud Run"
  type        = string
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

variable "memory" {
  description = "Memory allocation for Cloud Run service"
  type        = string
  default     = "2Gi"
}

variable "cpu" {
  description = "CPU allocation for Cloud Run service"
  type        = string
  default     = "2"
}

variable "allowed_ingress" {
  description = "Allowed ingress for Cloud Run service"
  type        = string
  default     = "all"
}

variable "service_account_email" {
  description = "Email of the service account used by the application"
  type        = string
}

variable "bucket_name" {
  description = "Name of the GCS bucket for images"
  type        = string
}

variable "mongodb_secret_id" {
  description = "Secret Manager secret ID for MongoDB URI"
  type        = string
}

variable "labels" {
  description = "Labels to apply to resources"
  type        = map(string)
  default     = {}
}
