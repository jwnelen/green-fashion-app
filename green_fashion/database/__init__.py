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

from .wardrobe_manager import WardrobeManager
from .data_loader import DataLoader

__all__ = ["WardrobeManager", "DataLoader"]
