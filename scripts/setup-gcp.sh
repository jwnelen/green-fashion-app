#!/bin/bash

# Setup script for Google Cloud Platform resources
# Run this script to set up your GCP project for the Green Fashion application

set -e

# Configuration
PROJECT_ID=${1:-""}
REGION=${2:-"us-central1"}
ENVIRONMENT=${3:-"dev"}

if [ -z "$PROJECT_ID" ]; then
    echo "Usage: $0 <PROJECT_ID> [REGION] [ENVIRONMENT]"
    echo "Example: $0 my-project-123 us-central1 dev"
    exit 1
fi

echo "🚀 Setting up Google Cloud Platform for Green Fashion"
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Environment: $ENVIRONMENT"

# Set the project
gcloud config set project "$PROJECT_ID"

# Enable required APIs
echo "📡 Enabling required APIs..."
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    containerregistry.googleapis.com \
    storage-api.googleapis.com \
    secretmanager.googleapis.com \
    monitoring.googleapis.com \
    logging.googleapis.com

# Create service account for application
SERVICE_ACCOUNT_NAME="green-fashion-$ENVIRONMENT"
SERVICE_ACCOUNT_EMAIL="$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com"

echo "🔐 Creating service account: $SERVICE_ACCOUNT_NAME"
if ! gcloud iam service-accounts describe "$SERVICE_ACCOUNT_EMAIL" >/dev/null 2>&1; then
    gcloud iam service-accounts create "$SERVICE_ACCOUNT_NAME" \
        --display-name="Green Fashion App Service Account ($ENVIRONMENT)" \
        --description="Service account for Green Fashion application in $ENVIRONMENT"
fi

# Assign necessary roles to the service account
echo "🛡️ Assigning IAM roles..."
for role in \
    "roles/storage.objectAdmin" \
    "roles/secretmanager.secretAccessor" \
    "roles/logging.logWriter" \
    "roles/monitoring.metricWriter" \
    "roles/trace.agent"; do

    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
        --role="$role"
done

# Create GCS bucket for images
BUCKET_NAME="green-fashion-$ENVIRONMENT-images"
echo "🪣 Creating GCS bucket: $BUCKET_NAME"
if ! gsutil ls "gs://$BUCKET_NAME" >/dev/null 2>&1; then
    gsutil mb -p "$PROJECT_ID" -c STANDARD -l "$REGION" "gs://$BUCKET_NAME"

    # Set bucket lifecycle (delete files after 30 days for dev, 365 for prod)
    LIFECYCLE_DAYS=30
    if [ "$ENVIRONMENT" = "prod" ]; then
        LIFECYCLE_DAYS=365
    fi

    cat > /tmp/lifecycle.json << EOF
{
  "rule": [
    {
      "action": {"type": "Delete"},
      "condition": {"age": $LIFECYCLE_DAYS}
    }
  ]
}
EOF
    gsutil lifecycle set /tmp/lifecycle.json "gs://$BUCKET_NAME"
    rm /tmp/lifecycle.json
fi

# Create service account key (for development only)
if [ "$ENVIRONMENT" = "dev" ]; then
    KEY_FILE="./gcs-key-$ENVIRONMENT.json"
    echo "🔑 Creating service account key: $KEY_FILE"
    gcloud iam service-accounts keys create "$KEY_FILE" \
        --iam-account="$SERVICE_ACCOUNT_EMAIL"

    echo "⚠️  IMPORTANT: Store the service account key securely!"
    echo "   Key file: $KEY_FILE"
    echo "   Add this to your .env file:"
    echo "   GCS_CREDENTIALS_PATH=$PWD/$KEY_FILE"
fi

# Create Terraform state bucket (optional)
STATE_BUCKET="$PROJECT_ID-terraform-state"
echo "🗂️  Creating Terraform state bucket: $STATE_BUCKET"
if ! gsutil ls "gs://$STATE_BUCKET" >/dev/null 2>&1; then
    gsutil mb -p "$PROJECT_ID" -c STANDARD -l "$REGION" "gs://$STATE_BUCKET"
    gsutil versioning set on "gs://$STATE_BUCKET"
fi

echo "✅ GCP setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Update your .env file with the following values:"
echo "   GCS_PROJECT_ID=$PROJECT_ID"
echo "   GCS_BUCKET_DEV=green-fashion-dev-images"
echo "   GCS_BUCKET_PROD=green-fashion-prod-images"
if [ "$ENVIRONMENT" = "dev" ]; then
    echo "   GCS_CREDENTIALS_PATH=$PWD/$KEY_FILE"
fi
echo ""
echo "2. Set up your MongoDB URI in Secret Manager:"
echo "   gcloud secrets create green-fashion-$ENVIRONMENT-mongodb-uri --data-file=-"
echo ""
echo "3. Configure your GitHub secrets for CI/CD:"
echo "   - GCP_PROJECT_ID: $PROJECT_ID"
echo "   - GCP_SA_KEY: (base64 encoded service account key)"
echo "   - MONGODB_URI: (your MongoDB connection string)"
