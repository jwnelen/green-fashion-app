"""
Data loading utilities for the Green Fashion project.

This module provides utilities for loading data from various sources,
including the parsed dataset JSON file and other data formats.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

from .config import DATASET_PATH


class DataLoader:
    """
    Utilities for loading data from various sources.

    This class provides methods to load clothing data from different
    file formats and sources.
    """

    @staticmethod
    def load_dataset_items(dataset_path: Optional[Path] = None) -> List[Dict]:
        """
        Load items from the parsed dataset JSON file.

        Args:
            dataset_path: Path to the dataset file (optional)

        Returns:
            List[Dict]: List of clothing items from the dataset
        """
        path = dataset_path or DATASET_PATH
        try:
            with open(path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Dataset file not found at: {path}")
            return []
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON file: {str(e)}")
            return []
        except Exception as e:
            print(f"Error loading dataset: {str(e)}")
            return []

    @staticmethod
    def load_json_file(file_path: Path) -> Optional[Dict]:
        """
        Load data from a JSON file.

        Args:
            file_path: Path to the JSON file

        Returns:
            Dict: Loaded data or None if failed
        """
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading JSON file {file_path}: {str(e)}")
            return None

    @staticmethod
    def save_json_file(data: Dict, file_path: Path) -> bool:
        """
        Save data to a JSON file.

        Args:
            data: Data to save
            file_path: Path where to save the file

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w") as f:
                json.dump(data, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error saving JSON file {file_path}: {str(e)}")
            return False

    @staticmethod
    def validate_item_data(item: Dict) -> bool:
        """
        Validate that an item has required fields.

        Args:
            item: Item dictionary to validate

        Returns:
            bool: True if valid, False otherwise
        """
        required_fields = ["category"]
        # optional_fields = [
        #     "custom_name",
        #     "display_name",
        #     "body_section",
        #     "colors",
        #     "path",
        #     "notes",
        # ]

        # Check required fields
        for field in required_fields:
            if field not in item:
                return False

        return True

    @staticmethod
    def clean_item_data(item: Dict) -> Dict:
        """
        Clean and standardize item data.

        Args:
            item: Raw item data

        Returns:
            Dict: Cleaned item data
        """
        cleaned = item.copy()

        # Ensure required fields have default values
        if "custom_name" not in cleaned and "display_name" in cleaned:
            cleaned["custom_name"] = cleaned["display_name"]

        if "custom_name" not in cleaned:
            cleaned["custom_name"] = "Unnamed Item"

        if "colors" not in cleaned:
            cleaned["colors"] = []

        if "body_section" not in cleaned:
            # Try to infer from category
            category = cleaned.get("category", "").lower()
            if category in ["hat"]:
                cleaned["body_section"] = 0  # Head
            elif category in ["shirt", "t-shirt", "longsleeve", "dress", "outwear"]:
                cleaned["body_section"] = 1  # Upper Body
            elif category in ["pants", "shorts", "skirt"]:
                cleaned["body_section"] = 2  # Lower Body
            elif category in ["shoes"]:
                cleaned["body_section"] = 3  # Feet
            else:
                cleaned["body_section"] = 1  # Default to Upper Body

        return cleaned

    @classmethod
    def load_and_clean_dataset(cls, dataset_path: Optional[Path] = None) -> List[Dict]:
        """
        Load dataset items and clean the data.

        Args:
            dataset_path: Path to the dataset file (optional)

        Returns:
            List[Dict]: List of cleaned clothing items
        """
        items = cls.load_dataset_items(dataset_path)
        cleaned_items = []

        for item in items:
            if cls.validate_item_data(item):
                cleaned_items.append(cls.clean_item_data(item))
            else:
                print(f"Skipping invalid item: {item.get('display_name', 'Unknown')}")

        return cleaned_items
