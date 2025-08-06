# Development environment configuration

environment = "dev"

# Scaling configuration - lower for dev
min_instances = 0
max_instances = 3

# Resource allocation - smaller for dev
memory = "1Gi"
cpu    = "1"

# Access control - public for dev testing
allowed_ingress = "all"

# Monitoring - enabled but less aggressive
enable_monitoring = true
enable_cdn       = false

# Custom domain (optional)
custom_domain = ""
