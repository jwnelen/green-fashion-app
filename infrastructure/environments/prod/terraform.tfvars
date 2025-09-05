# Production environment configuration
project_id = "clothing-manager-468218"
environment = "prod"

# Optional: Service account to impersonate for Terraform operations
# Note: Secrets like service account keys should be set via GitHub secrets or environment variables

# Scaling configuration - production ready
min_instances = 0
max_instances = 2

# Resource allocation - production specs
api_memory = "1Gi"
classifier_memory = "2Gi"
api_cpu = "1"
classifier_cpu = "2"

# Access control - public for production
allowed_ingress = "all"

# CDN - enabled for production
enable_cdn = true

# Custom domain
custom_domain = "" # e.g., "green-fashion.example.com"

# Storage configuration - production settings
bucket_versioning_enabled = true
bucket_lifecycle_age_days = 30

# Container images (dummy values for refresh)
container_image = "gcr.io/clothing-manager-468218/green-fashion:latest"
classifier_api_container_image = "gcr.io/clothing-manager-468218/classifier-api:latest"
