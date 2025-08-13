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

variable "labels" {
  description = "Labels to apply to resources"
  type        = map(string)
  default     = {}
}
