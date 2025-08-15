from datetime import datetime
from typing import Dict, List, Optional

from bson import ObjectId
from pymongo import MongoClient

from .config import (
    CLOTHING_ITEMS_DB_NAME,
    DATABASE_NAME,
    USER_DB_NAME,
    WARDROBE_IMAGES_DIR,
)


class MongoDBManager:
    """
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
        self.mongodb_uri = mongodb_uri
        self.database_name = database_name or DATABASE_NAME

        self.client = None
        self.db = None
        self.clothing_items_db = None
        self.user_db = None
        self.connection_error = None

        self.connect_to_db()
        self.ensure_image_directory()

    def connect_to_db(self) -> bool:
        """
        Establish connection to MongoDB.

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.client = MongoClient(
                self.mongodb_uri,
                serverSelectionTimeoutMS=4000,  # 2 second timeout
                connectTimeoutMS=4000,  # 2 second connection timeout
                socketTimeoutMS=4000,  # 2 second socket timeout
            )
            self.db = self.client[self.database_name]
            self.clothing_items_db = self.db[CLOTHING_ITEMS_DB_NAME]
            self.user_db = self.db[USER_DB_NAME]

            # Test connection
            self.client.server_info()
            return True
        except Exception as e:
            print(f"Failed to connect to MongoDB: {str(e)}")
            self.connection_error = str(e)
            self.client = None
            self.db = None
            self.clothing_items_db = None
            self.user_db = None
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
            result = self.clothing_items_db.insert_one(item_data)
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
            items = list(self.clothing_items_db.find())
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
            item = self.clothing_items_db.find_one({"_id": ObjectId(item_id)})
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
            result = self.clothing_items_db.update_one(
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
            result = self.clothing_items_db.delete_one({"_id": ObjectId(item_id)})
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
                self.clothing_items_db.find(
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
            items = list(self.clothing_items_db.find({"category": category}))
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
            return self.clothing_items_db.distinct("category")
        except Exception as e:
            print(f"Error fetching categories: {str(e)}")
            return []

    def get_item_count(self) -> int:
        """
        Get total number of items in the wardrobe.

        Returns:
            int: Total item count
        """
        try:
            return self.clothing_items_db.count_documents({})
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
            results = list(self.clothing_items_db.aggregate(pipeline))
            return {result["_id"]: result["count"] for result in results}
        except Exception as e:
            print(f"Error getting category counts: {str(e)}")
            return {}

    def create_or_get_user(self, google_user_data):
        existing_user = self.user_db.find_one(
            {"google_id": google_user_data["google_id"]}
        )

        if existing_user:
            self.user_db.update_one(
                {"_id": existing_user["_id"]},
                {"$set": {"last_login": datetime.utcnow()}},
            )
            return existing_user

        user_doc = {
            "google_id": google_user_data["google_id"],
            "email": google_user_data["email"],
            "name": google_user_data["name"],
            "picture": google_user_data.get("picture"),
            "created_at": datetime.utcnow(),
            "last_login": datetime.utcnow(),
        }

        result = self.user_db.insert_one(user_doc)
        user_doc["_id"] = result.inserted_id
        return user_doc

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close connection."""
        self.close_connection()
