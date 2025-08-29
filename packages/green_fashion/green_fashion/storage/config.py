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

# Storage paths within buckets (kept for reference but no longer used by GCS service)
IMAGES_PATH = "images"
