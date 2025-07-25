"""
MongoDB-based wardrobe management system.

This module provides CRUD operations for managing clothing items in a MongoDB database,
including image file management and search functionality.
"""

import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from bson import ObjectId
from pymongo import MongoClient

from .config import MONGODB_URI, DATABASE_NAME, COLLECTION_NAME, WARDROBE_IMAGES_DIR


class WardrobeManager:
    """
    Manages wardrobe items in MongoDB with file storage capabilities.

    This class provides comprehensive CRUD operations for clothing items,
    including image management and search functionality.

    Attributes:
        client: MongoDB client instance
        db: Database instance
        collection: Collection instance for clothing items
    """

    def __init__(self, mongodb_uri: str = None, database_name: str = None):
        """
        Initialize the wardrobe manager.

        Args:
            mongodb_uri: MongoDB connection string (optional)
            database_name: Database name (optional)
        """
        self.mongodb_uri = mongodb_uri or MONGODB_URI
        self.database_name = database_name or DATABASE_NAME
        self.collection_name = COLLECTION_NAME

        self.client = None
        self.db = None
        self.collection = None

        self.connect_to_db()
        self.ensure_image_directory()

    def connect_to_db(self) -> bool:
        """
        Establish connection to MongoDB.

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.client = MongoClient(self.mongodb_uri)
            self.db = self.client[self.database_name]
            self.collection = self.db[self.collection_name]

            # Test connection
            self.client.server_info()
            return True
        except Exception as e:
            print(f"Failed to connect to MongoDB: {str(e)}")
            return False

    def close_connection(self):
        """Close the MongoDB connection."""
        if self.client:
            self.client.close()

    def ensure_image_directory(self):
        """Ensure the wardrobe images directory exists."""
        try:
            WARDROBE_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Error creating image directory: {str(e)}")

    # CRUD Operations

    def add_clothing_item(self, item_data: Dict) -> Optional[str]:
        """
        Add a new clothing item to the database.

        Args:
            item_data: Dictionary containing item information

        Returns:
            str: The inserted item's ID, or None if failed
        """
        try:
            item_data["created_at"] = datetime.now()
            item_data["updated_at"] = datetime.now()
            result = self.collection.insert_one(item_data)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error adding item: {str(e)}")
            return None

    def get_all_items(self) -> List[Dict]:
        """
        Retrieve all clothing items from the database.

        Returns:
            List[Dict]: List of all clothing items
        """
        try:
            items = list(self.collection.find())
            for item in items:
                item["_id"] = str(item["_id"])
            return items
        except Exception as e:
            print(f"Error fetching items: {str(e)}")
            return []

    def get_item_by_id(self, item_id: str) -> Optional[Dict]:
        """
        Retrieve a specific item by its ID.

        Args:
            item_id: The item's ID

        Returns:
            Dict: Item data or None if not found
        """
        try:
            item = self.collection.find_one({"_id": ObjectId(item_id)})
            if item:
                item["_id"] = str(item["_id"])
            return item
        except Exception as e:
            print(f"Error fetching item: {str(e)}")
            return None

    def update_item(self, item_id: str, updates: Dict) -> bool:
        """
        Update an existing clothing item.

        Args:
            item_id: The item's ID
            updates: Dictionary of fields to update

        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            updates["updated_at"] = datetime.now()
            result = self.collection.update_one(
                {"_id": ObjectId(item_id)}, {"$set": updates}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating item: {str(e)}")
            return False

    def delete_item(self, item_id: str) -> bool:
        """
        Delete a clothing item and its associated image file.

        Args:
            item_id: The item's ID

        Returns:
            bool: True if deletion successful, False otherwise
        """
        try:
            # First get the item to check if it has an image
            item = self.collection.find_one({"_id": ObjectId(item_id)})
            if item and item.get("path"):
                # Only delete uploaded images (in wardrobe directory)
                if "wardrobe" in item["path"]:
                    self.delete_image_file(item["path"])

            result = self.collection.delete_one({"_id": ObjectId(item_id)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting item: {str(e)}")
            return False

    # Search Operations

    def search_items(self, query: str) -> List[Dict]:
        """
        Search for items based on name, category, or filename.

        Args:
            query: Search query string

        Returns:
            List[Dict]: List of matching items
        """
        try:
            items = list(
                self.collection.find(
                    {
                        "$or": [
                            {"custom_name": {"$regex": query, "$options": "i"}},
                            {"category": {"$regex": query, "$options": "i"}},
                            {"display_name": {"$regex": query, "$options": "i"}},
                        ]
                    }
                )
            )
            for item in items:
                item["_id"] = str(item["_id"])
            return items
        except Exception as e:
            print(f"Error searching items: {str(e)}")
            return []

    def get_items_by_category(self, category: str) -> List[Dict]:
        """
        Get all items in a specific category.

        Args:
            category: Category name

        Returns:
            List[Dict]: List of items in the category
        """
        try:
            items = list(self.collection.find({"category": category}))
            for item in items:
                item["_id"] = str(item["_id"])
            return items
        except Exception as e:
            print(f"Error fetching items by category: {str(e)}")
            return []

    def get_categories(self) -> List[str]:
        """
        Get all unique categories in the database.

        Returns:
            List[str]: List of unique categories
        """
        try:
            return self.collection.distinct("category")
        except Exception as e:
            print(f"Error fetching categories: {str(e)}")
            return []

    # Image Management

    def save_uploaded_image(self, uploaded_file, category: str) -> Optional[str]:
        """
        Save an uploaded image file and return the file path.

        Args:
            uploaded_file: Uploaded file object
            category: Item category for organizing files

        Returns:
            str: File path if successful, None otherwise
        """
        try:
            # Generate unique filename
            file_extension = uploaded_file.name.split(".")[-1].lower()
            unique_filename = f"{uuid.uuid4()}.{file_extension}"

            # Create category subdirectory if it doesn't exist
            category_dir = WARDROBE_IMAGES_DIR / category
            category_dir.mkdir(exist_ok=True)

            # Full path for the image
            image_path = category_dir / unique_filename

            # Save the image
            with open(image_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            return str(image_path)
        except Exception as e:
            print(f"Error saving image: {str(e)}")
            return None

    def delete_image_file(self, image_path: str) -> bool:
        """
        Delete an image file from the filesystem.

        Args:
            image_path: Path to the image file

        Returns:
            bool: True if deletion successful, False otherwise
        """
        try:
            if image_path and os.path.exists(image_path):
                os.remove(image_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting image file: {str(e)}")
            return False

    # Bulk Operations

    def bulk_import_items(self, items: List[Dict]) -> int:
        """
        Import multiple items in bulk.

        Args:
            items: List of item dictionaries to import

        Returns:
            int: Number of items successfully imported
        """
        imported_count = 0
        for item in items:
            # Check if item already exists (by path)
            existing = list(self.collection.find({"path": item.get("path")}))
            if not existing:
                if self.add_clothing_item(item):
                    imported_count += 1
        return imported_count

    # Statistics

    def get_item_count(self) -> int:
        """
        Get total number of items in the wardrobe.

        Returns:
            int: Total item count
        """
        try:
            return self.collection.count_documents({})
        except Exception as e:
            print(f"Error getting item count: {str(e)}")
            return 0

    def get_category_counts(self) -> Dict[str, int]:
        """
        Get count of items per category.

        Returns:
            Dict[str, int]: Category counts
        """
        try:
            pipeline = [
                {"$group": {"_id": "$category", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
            ]
            results = list(self.collection.aggregate(pipeline))
            return {result["_id"]: result["count"] for result in results}
        except Exception as e:
            print(f"Error getting category counts: {str(e)}")
            return {}

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close connection."""
        self.close_connection()
