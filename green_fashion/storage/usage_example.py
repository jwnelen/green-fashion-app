"""
Example usage of the GCS service for image operations.
"""

from pathlib import Path
from PIL import Image
from .gcs_service import get_gcs_service


def example_usage():
    """Example of how to use the GCS service."""
    # Get the service instance
    gcs = get_gcs_service()

    # Example 1: Save an image from file path
    image_path = Path("path/to/your/image.jpg")
    if image_path.exists():
        gcs_path = gcs.save_image(
            image=image_path, filename="my-clothing-item-001", category="wardrobe"
        )
        print(f"Image saved to: {gcs_path}")

    # Example 2: Save a PIL Image
    # Create a sample image (or load from elsewhere)
    sample_image = Image.new("RGB", (100, 100), color="red")
    gcs_path = gcs.save_image(
        image=sample_image, filename="sample-red-square", category="wardrobe"
    )
    print(f"Sample image saved to: {gcs_path}")

    # Example 3: Load an image
    try:
        loaded_image = gcs.load_image(gcs_path)
        print(f"Loaded image size: {loaded_image.size}")
    except Exception as e:
        print(f"Failed to load image: {e}")

    # Example 4: Check if image exists
    exists = gcs.image_exists(gcs_path)
    print(f"Image exists: {exists}")

    # Example 5: List images in wardrobe
    image_paths = gcs.list_images(category="wardrobe")
    print(f"Found {len(image_paths)} images in wardrobe")

    # Example 6: Delete an image
    deleted = gcs.delete_image(gcs_path)
    print(f"Image deleted: {deleted}")


if __name__ == "__main__":
    example_usage()
