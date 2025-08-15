"""
Google Cloud Storage service for handling image operations.
"""

import io
import os
from pathlib import Path
from typing import Optional, Union

from google.cloud import storage
from google.cloud.exceptions import GoogleCloudError, NotFound
from PIL import Image

from .config import (
    DATASET_IMAGES_PATH,
    GCS_CREDENTIALS_PATH,
    GCS_PROJECT_ID,
    WARDROBE_IMAGES_PATH,
)


class GCSService:
    """Google Cloud Storage service for image operations."""

    def __init__(self, bucket_name):
        """Initialize GCS client."""
        self._bucket_name = bucket_name
        self._client = None
        self._bucket = None

    @property
    def client(self) -> storage.Client:
        """Get or create GCS client."""
        if self._client is None:
            if GCS_CREDENTIALS_PATH and os.path.exists(GCS_CREDENTIALS_PATH):
                print(
                    f"Debug: Using service account credentials from {GCS_CREDENTIALS_PATH}"
                )
                self._client = storage.Client.from_service_account_json(
                    GCS_CREDENTIALS_PATH, project=GCS_PROJECT_ID
                )
            else:
                # Use default credentials (e.g., from environment)
                self._client = storage.Client(project=GCS_PROJECT_ID)
        return self._client

    @property
    def bucket(self) -> storage.Bucket:
        """Get or create bucket reference."""
        if self._bucket is None:
            self._bucket = self.client.bucket(self._bucket_name)
        return self._bucket

    def save_image(
        self,
        image: Union[Image.Image, str, Path],
        filename: str,
        category: str = "wardrobe",
        quality: int = 95,
    ) -> str:
        """
        Save an image to Google Cloud Storage.

        Args:
            image: PIL Image, file path, or image data
            filename: Name for the saved file (without extension)
            category: Category folder ('wardrobe' or 'dataset')
            quality: JPEG quality (1-100)

        Returns:
            str: GCS path of the saved image

        Raises:
            GoogleCloudError: If upload fails
            ValueError: If image format is invalid
        """
        try:
            # Determine the storage path based on category
            if category == "dataset":
                storage_path = DATASET_IMAGES_PATH
            else:
                storage_path = WARDROBE_IMAGES_PATH

            # Ensure filename has .jpg extension
            if not filename.lower().endswith(".jpg"):
                filename = f"{filename}.jpg"

            blob_name = f"{storage_path}/{filename}"

            # Convert image to bytes
            image_bytes = self._prepare_image_bytes(image, quality)

            # Upload to GCS
            blob = self.bucket.blob(blob_name)
            blob.upload_from_string(image_bytes, content_type="image/jpeg")

            return blob_name

        except Exception as e:
            raise GoogleCloudError(f"Failed to save image: {str(e)}")

    def load_image(self, gcs_path: str) -> Image.Image:
        """
        Load an image from Google Cloud Storage.

        Args:
            gcs_path: GCS path of the image

        Returns:
            PIL.Image.Image: Loaded image

        Raises:
            NotFound: If image doesn't exist
            GoogleCloudError: If download fails
        """
        try:
            blob = self.bucket.blob(gcs_path)

            if not blob.exists():
                raise NotFound(f"Image not found: {gcs_path}")

            # Download image data
            image_data = blob.download_as_bytes()

            # Convert to PIL Image
            image = Image.open(io.BytesIO(image_data))
            return image

        except NotFound:
            raise
        except Exception as e:
            raise GoogleCloudError(f"Failed to load image: {str(e)}")

    def delete_image(self, gcs_path: str) -> bool:
        """
        Delete an image from Google Cloud Storage.

        Args:
            gcs_path: GCS path of the image to delete

        Returns:
            bool: True if deleted successfully, False if not found

        Raises:
            GoogleCloudError: If deletion fails
        """
        try:
            blob = self.bucket.blob(gcs_path)

            if not blob.exists():
                return False

            blob.delete()
            return True

        except Exception as e:
            raise GoogleCloudError(f"Failed to delete image: {str(e)}")

    def image_exists(self, gcs_path: str) -> bool:
        """
        Check if an image exists in Google Cloud Storage.

        Args:
            gcs_path: GCS path of the image

        Returns:
            bool: True if image exists, False otherwise
        """
        try:
            blob = self.bucket.blob(gcs_path)
            return blob.exists()
        except Exception:
            return False

    def get_public_url(self, gcs_path: str) -> str:
        """
        Get the public URL for a GCS object.

        Args:
            gcs_path: GCS path of the image

        Returns:
            str: Public URL of the image
        """
        blob = self.bucket.blob(gcs_path)
        return blob.public_url

    def list_images(
        self, category: str = "wardrobe", prefix: Optional[str] = None
    ) -> list[str]:
        """
        List images in a category folder.

        Args:
            category: Category folder ('wardrobe' or 'dataset')
            prefix: Optional prefix to filter by

        Returns:
            list[str]: List of GCS paths
        """
        try:
            if category == "dataset":
                storage_path = DATASET_IMAGES_PATH
            else:
                storage_path = WARDROBE_IMAGES_PATH

            if prefix:
                full_prefix = f"{storage_path}/{prefix}"
            else:
                full_prefix = f"{storage_path}/"

            blobs = self.client.list_blobs(self.bucket, prefix=full_prefix)
            return [blob.name for blob in blobs if blob.name.endswith(".jpg")]

        except Exception as e:
            raise GoogleCloudError(f"Failed to list images: {str(e)}")

    def _prepare_image_bytes(
        self, image: Union[Image.Image, str, Path], quality: int
    ) -> bytes:
        """
        Prepare image data as bytes for upload.

        Args:
            image: PIL Image, file path, or uploaded file object
            quality: JPEG quality

        Returns:
            bytes: Image data as bytes
        """
        if isinstance(image, (str, Path)):
            # Load from file path
            img = Image.open(image)
        elif isinstance(image, Image.Image):
            img = image
        elif hasattr(image, "read"):
            # Handle file-like objects (e.g., Streamlit UploadedFile)
            img = Image.open(image)
        else:
            raise ValueError("Image must be PIL Image, file path, or file-like object")

        # Convert to RGB if necessary
        if img.mode != "RGB":
            img = img.convert("RGB")

        # Convert to bytes
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=quality)
        return buffer.getvalue()


# Singleton instance
_gcs_service = None


def get_gcs_service(bucket_name) -> GCSService:
    """Get singleton GCS service instance."""
    global _gcs_service
    if _gcs_service is None:
        _gcs_service = GCSService(bucket_name)
    return _gcs_service
