# Development environment configuration

environment = "dev"

# Optional: Service account to impersonate for Terraform operations
impersonate_service_account = "terraform@clothing-manager-468218.iam.gserviceaccount.com"

# Scaling configuration - lower for dev
min_instances = 0
max_instances = 3

# Resource allocation - smaller for dev
memory = "1Gi"
cpu    = "1"

# Access control - public for dev testing
allowed_ingress = "all"

# CDN - disabled for dev
enable_cdn = false

# Custom domain (optional)
custom_domain = ""
