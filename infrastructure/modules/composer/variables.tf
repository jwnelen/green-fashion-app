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

variable "zone" {
  description = "Google Cloud zone"
  type        = string
  default     = "europe-west4-a"
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

variable "machine_type" {
  description = "Machine type for Composer nodes"
  type        = string
  default     = "n1-standard-1"
}

variable "disk_size_gb" {
  description = "Disk size in GB for Composer nodes"
  type        = number
  default     = 100
}

variable "network" {
  description = "VPC network for Composer"
  type        = string
  default     = "default"
}

variable "subnetwork" {
  description = "Subnetwork for Composer"
  type        = string
  default     = null
}

variable "database_machine_type" {
  description = "Machine type for the database"
  type        = string
  default     = "db-n1-standard-2"
}

variable "web_server_machine_type" {
  description = "Machine type for the web server"
  type        = string
  default     = "composer-n1-webserver-2"
}


variable "scheduler_cpu" {
  description = "CPU allocation for scheduler"
  type        = number
  default     = 0.5
}

variable "scheduler_memory_gb" {
  description = "Memory allocation for scheduler in GB"
  type        = number
  default     = 1.875
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
  description = "Memory allocation for web server in GB"
  type        = number
  default     = 1.875
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
  description = "Memory allocation for workers in GB"
  type        = number
  default     = 1.875
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
