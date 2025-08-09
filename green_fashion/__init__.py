"""
Green Fashion - Main package

This package contains all the core functionality for the Green Fashion project,
including color extraction, database management, and clothing classification.
"""

__version__ = "0.1.0"

# Make key classes easily importable
from .database import DataLoader, MongoDBManager

__all__ = ["MongoDBManager", "DataLoader"]
