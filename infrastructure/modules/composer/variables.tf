variable "service_name" {
  description = "Name of the service"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "project_id" {
  description = "Google Cloud Project ID"
  type        = string
}

variable "region" {
  description = "Google Cloud region"
  type        = string
  default     = "europe-west4"
}

variable "labels" {
  description = "Labels to apply to resources"
  type        = map(string)
  default     = {}
}

variable "airflow_image_version" {
  description = "Airflow image version for Cloud Composer"
  type        = string
  default     = "composer-3-airflow-2.10.5-build.14"
}


variable "scheduler_cpu" {
  description = "CPU allocation for scheduler"
  type        = number
  default     = 0.5
}

variable "scheduler_memory_gb" {
  description = "Memory allocation for scheduler in GB (must be multiple of 0.25)"
  type        = number
  default     = 2.0
}

variable "scheduler_storage_gb" {
  description = "Storage allocation for scheduler in GB"
  type        = number
  default     = 1
}

variable "scheduler_count" {
  description = "Number of schedulers"
  type        = number
  default     = 1
}

variable "web_server_cpu" {
  description = "CPU allocation for web server"
  type        = number
  default     = 0.5
}

variable "web_server_memory_gb" {
  description = "Memory allocation for web server in GB (must be at least 2GB)"
  type        = number
  default     = 2.0
}

variable "web_server_storage_gb" {
  description = "Storage allocation for web server in GB"
  type        = number
  default     = 1
}

variable "worker_cpu" {
  description = "CPU allocation for workers"
  type        = number
  default     = 0.5
}

variable "worker_memory_gb" {
  description = "Memory allocation for workers in GB (must be multiple of 0.25)"
  type        = number
  default     = 2.0
}

variable "worker_storage_gb" {
  description = "Storage allocation for workers in GB"
  type        = number
  default     = 1
}

variable "worker_min_count" {
  description = "Minimum number of workers"
  type        = number
  default     = 1
}

variable "worker_max_count" {
  description = "Maximum number of workers"
  type        = number
  default     = 3
}

variable "airflow_env_variables" {
  description = "Environment variables for Airflow"
  type        = map(string)
  default     = {}
}

variable "pypi_packages" {
  description = "PyPI packages to install in the environment"
  type        = map(string)
  default     = {}
}
