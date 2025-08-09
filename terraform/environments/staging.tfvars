# Staging environment configuration

environment = "staging"

# Scaling configuration - moderate for staging
min_instances = 1
max_instances = 5

# Resource allocation - moderate for staging
memory = "2Gi"
cpu    = "1"

# Access control - internal for staging
allowed_ingress = "internal-and-cloud-load-balancing"

# CDN - disabled for staging
enable_cdn = false

# Custom domain (optional)
custom_domain = "" # e.g., "staging.green-fashion.example.com"
