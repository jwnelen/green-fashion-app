"""
Database configuration settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB Configuration
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
DATABASE_NAME = "wardrobe_db"
COLLECTION_NAME = "clothing_items"

# File storage configuration
BASE_DIR = Path(__file__).parent.parent.parent
WARDROBE_IMAGES_DIR = BASE_DIR / "artifacts" / "images" / "wardrobe"
DATASET_PATH = BASE_DIR / "artifacts" / "datasets" / "dataset_all_colors_parsed.json"

# Categories for clothing items
CLOTHING_CATEGORIES = [
    "dress",
    "shirt",
    "t-shirt",
    "longsleeve",
    "pants",
    "shorts",
    "skirt",
    "shoes",
    "hat",
    "outwear",
    "other",
]

# Body sections mapping
BODY_SECTIONS = {0: "Head", 1: "Upper Body", 2: "Lower Body", 3: "Feet"}
