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

from .config import GCS_CREDENTIALS_PATH, GCS_PROJECT_ID


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
        blob_path: str,
        quality: int = 95,
    ) -> str:
        """
        Save an image to Google Cloud Storage.

        Args:
            image: PIL Image, file path, or image data
            blob_path: Full GCS blob path (e.g., "images/wardrobe/filename.jpg")
            quality: JPEG quality (1-100)

        Returns:
            str: GCS path of the saved image

        Raises:
            GoogleCloudError: If upload fails
            ValueError: If image format is invalid
        """
        try:
            # Ensure the path has .jpg extension
            if not blob_path.lower().endswith(".jpg"):
                blob_path = f"{blob_path}.jpg"

            # Convert image to bytes
            image_bytes = self._prepare_image_bytes(image, quality)

            # Upload to GCS
            blob = self.bucket.blob(blob_path)
            blob.upload_from_string(image_bytes, content_type="image/jpeg")

            return blob_path

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

    def list_images(self, prefix: Optional[str] = None) -> list[str]:
        """
        List images with optional prefix filter.

        Args:
            prefix: Optional prefix to filter by (e.g., "images/wardrobe/")

        Returns:
            list[str]: List of GCS paths
        """
        try:
            blobs = self.client.list_blobs(self.bucket, prefix=prefix)
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

        # Handle EXIF orientation (fixes iPhone rotation issues)
        try:
            # Get EXIF data
            exif = img._getexif()
            if exif is not None:
                # Look for orientation tag (274)
                orientation = exif.get(274)
                if orientation == 3:
                    img = img.rotate(180, expand=True)
                elif orientation == 6:
                    img = img.rotate(270, expand=True)
                elif orientation == 8:
                    img = img.rotate(90, expand=True)
        except (AttributeError, KeyError, TypeError):
            # If EXIF data is not available or corrupted, continue without rotation
            pass

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
