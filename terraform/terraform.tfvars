# Example Terraform variables file
# Copy this to terraform.tfvars and fill in your values

project_id = "clothing-manager-468218"
region     = "us-central1"
zone       = "us-central1-a"

environment = "dev" # or "staging" or "prod"

# Container image (will be updated by CI/CD)
container_image = "gcr.io/clothing-manager-468218/green-fashion:latest"

# Scaling configuration
min_instances = 0
max_instances = 10

# Resource allocation
memory = "2Gi"
cpu    = "2"

# MongoDB connection string (sensitive)
mongodb_uri = "mongodb+srv://username:password@cluster.mongodb.net/wardrobe_db"

# Access control
allowed_ingress = "all" # "all", "internal", or "internal-and-cloud-load-balancing"

# Optional custom domain
custom_domain = "" # e.g., "green-fashion.example.com"

# Monitoring
enable_cdn       = false
