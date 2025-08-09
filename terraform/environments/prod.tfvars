# Production environment configuration

environment = "prod"

# Optional: Service account to impersonate for Terraform operations
# impersonate_service_account = "terraform-prod@your-project-id.iam.gserviceaccount.com"

# Scaling configuration - production ready
min_instances = 2
max_instances = 20

# Resource allocation - production specs
memory = "4Gi"
cpu    = "2"

# Access control - public for production
allowed_ingress = "all"

# CDN - enabled for production
enable_cdn = true

# Custom domain
custom_domain = "" # e.g., "green-fashion.example.com"
