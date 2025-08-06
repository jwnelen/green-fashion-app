# Production environment configuration

environment = "prod"

# Scaling configuration - production ready
min_instances = 2
max_instances = 20

# Resource allocation - production specs
memory = "4Gi"
cpu    = "2"

# Access control - public for production
allowed_ingress = "all"

# Monitoring - comprehensive monitoring for production
enable_monitoring = true
enable_cdn       = true

# Custom domain
custom_domain = "" # e.g., "green-fashion.example.com"
