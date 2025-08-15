"""
Google Cloud Storage configuration settings.
"""

import os

# Load environment variables - don't call load_dotenv() here
# Let the calling application (like main.py) handle loading the .env file

# Google Cloud Storage Configuration
GCS_CREDENTIALS_PATH = os.getenv("GCS_CREDENTIALS_PATH")
GCS_PROJECT_ID = os.getenv("GCS_PROJECT_ID")

# Bucket name (set by Cloud Run environment)
GCS_IMAGE_BUCKET = os.getenv("GCS_IMAGE_BUCKET")

# Current environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")


# # Get the bucket name
# def get_bucket_name() -> str:
#     """Get the bucket name from environment variable."""
#     if not GCS_IMAGE_BUCKET:
#         raise ValueError("GCS_BUCKET_NAME environment variable must be set")
#     return GCS_IMAGE_BUCKET


# Storage paths within buckets
IMAGES_PATH = "images"
WARDROBE_IMAGES_PATH = f"{IMAGES_PATH}/wardrobe"
DATASET_IMAGES_PATH = f"{IMAGES_PATH}/dataset"
