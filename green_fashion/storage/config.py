"""
Google Cloud Storage configuration settings.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Google Cloud Storage Configuration
GCS_CREDENTIALS_PATH = os.getenv("GCS_CREDENTIALS_PATH")
GCS_PROJECT_ID = os.getenv("GCS_PROJECT_ID")

# Bucket names for different environments
GCS_BUCKET_DEV = os.getenv("GCS_BUCKET_DEV", "green-fashion-dev")
GCS_BUCKET_PROD = os.getenv("GCS_BUCKET_PROD", "green-fashion-prod")

# Current environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")


# Get the appropriate bucket based on environment
def get_bucket_name() -> str:
    """Get the bucket name for the current environment."""
    if ENVIRONMENT.lower() == "prod":
        return GCS_BUCKET_PROD
    return GCS_BUCKET_DEV


# Storage paths within buckets
IMAGES_PATH = "images"
WARDROBE_IMAGES_PATH = f"{IMAGES_PATH}/wardrobe"
DATASET_IMAGES_PATH = f"{IMAGES_PATH}/dataset"
