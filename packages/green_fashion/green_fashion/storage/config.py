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

# Bucket name (set by Cloud Run environment)
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")

# Current environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")


# Get the bucket name
def get_bucket_name() -> str:
    """Get the bucket name from environment variable."""
    if not GCS_BUCKET_NAME:
        raise ValueError("GCS_BUCKET_NAME environment variable must be set")
    return GCS_BUCKET_NAME


# Storage paths within buckets
IMAGES_PATH = "images"
WARDROBE_IMAGES_PATH = f"{IMAGES_PATH}/wardrobe"
DATASET_IMAGES_PATH = f"{IMAGES_PATH}/dataset"
