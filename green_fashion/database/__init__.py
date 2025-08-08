"""
Database module for Green Fashion project.

This module provides database management functionality including:
- MongoDB connection management
- CRUD operations for clothing items
- Image file management
- Data loading utilities

Usage:
    from src.database import WardrobeManager

    wm = WardrobeManager()
    items = wm.get_all_items()
"""

from .data_loader import DataLoader
from .mongodb_manager import MongoDBManager

__all__ = ["MongoDBManager", "DataLoader"]
