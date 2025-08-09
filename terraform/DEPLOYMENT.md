# Green Fashion Terraform Deployment Guide

This directory contains the Terraform infrastructure code for the Green Fashion application, configured to support multiple environments (dev, prod) within the same GCP project.

## Directory Structure

```
terraform/
├── main.tf                    # Main Terraform configuration
├── variables.tf               # Variable definitions
├── storage.tf                 # GCS bucket and IAM configuration
├── cloud_run.tf              # Cloud Run service configuration
├── secrets.tf                # Secret Manager configuration
├── monitoring.tf             # Monitoring and logging setup
├── outputs.tf                # Output values
├── deploy.sh                 # Deployment script
├── environments/             # Environment-specific configurations
│   ├── dev.tfvars           # Development variables
│   ├── prod.tfvars          # Production variables
│   ├── dev.backend.conf     # Development backend config
│   └── prod.backend.conf    # Production backend config
└── DEPLOYMENT.md            # This file
```

## Environment Configuration

### Development Environment
- **Bucket naming**: `green-fashion-dev-images`
- **Service naming**: `green-fashion-dev`
- **Scaling**: Min 0, Max 3 instances
- **Resources**: 1 vCPU, 1Gi memory
- **Storage**: No versioning, 30-day lifecycle
- **Protection**: Deletion protection disabled

### Production Environment
- **Bucket naming**: `green-fashion-prod-images`
- **Service naming**: `green-fashion-prod`
- **Scaling**: Min 2, Max 20 instances
- **Resources**: 2 vCPU, 4Gi memory
- **Storage**: Versioning enabled, 365-day lifecycle
- **Protection**: Deletion protection enabled

## Prerequisites

1. **GCP Project**: `clothing-manager-468218`
2. **Terraform State Bucket**: `green-fashion-terraform-state`
3. **Service Account**: Properly configured for Terraform operations
4. **Required APIs**: Enabled via Terraform (first run)

## Deployment Commands

### Using the Deploy Script (Recommended)

```bash
# Initialize environment
./deploy.sh dev init

# Plan deployment
./deploy.sh dev plan
./deploy.sh prod plan

# Apply changes
./deploy.sh dev apply
./deploy.sh prod apply

# Destroy infrastructure
./deploy.sh dev destroy
./deploy.sh prod destroy
```

### Manual Terraform Commands

```bash
# Initialize with environment-specific backend
terraform init -backend-config="environments/dev.backend.conf"

# Plan deployment
terraform plan -var-file="environments/dev.tfvars" -out="dev.tfplan"

# Apply deployment
terraform apply "dev.tfplan"

# Destroy infrastructure
terraform destroy -var-file="environments/dev.tfvars"
```

## State Management

Each environment maintains separate Terraform state files:
- **Dev state**: `gs://green-fashion-terraform-state/environments/dev/`
- **Prod state**: `gs://green-fashion-terraform-state/environments/prod/`

This isolation ensures that changes in one environment don't affect the other.

## Environment Variables

The following environment variables are automatically set in Cloud Run:

- `ENVIRONMENT`: Current environment (dev/prod)
- `GCS_PROJECT_ID`: GCP project ID
- `GCS_BUCKET_NAME`: Environment-specific bucket name
- `MONGODB_URI`: MongoDB connection string (from Secret Manager)

## Security Considerations

1. **Service Accounts**: Each environment uses its own service account
2. **IAM Roles**: Minimal required permissions
3. **Secrets**: Managed via Google Secret Manager
4. **Network Access**: Public access for Cloud Run (adjust as needed)
5. **Deletion Protection**: Enabled for production resources

## Monitoring

Both environments include:
- Cloud Logging integration
- Cloud Monitoring metrics
- Health check endpoints (`/health`)
- Startup and liveness probes

## Troubleshooting

### Common Issues

1. **State Lock**: If Terraform state is locked, wait or manually release
2. **Backend Config**: Ensure backend config files exist and are correct
3. **Service Account**: Verify permissions for Terraform service account
4. **API Enablement**: First deployment may take longer due to API activation

### Useful Commands

```bash
# Check current workspace and state
terraform workspace show
terraform state list

# Import existing resources (if needed)
terraform import google_storage_bucket.images_bucket green-fashion-dev-images

# Refresh state
terraform refresh -var-file="environments/dev.tfvars"
```

## Best Practices

1. Always run `terraform plan` before `terraform apply`
2. Use the deployment script for consistency
3. Keep environment-specific configurations in tfvars files
4. Review changes carefully in production
5. Test changes in dev environment first
6. Monitor resource usage and costs
