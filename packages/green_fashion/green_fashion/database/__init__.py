"""
Database module for Green Fashion project.

This module provides database management functionality including:
- MongoDB connection management
- SQL database connectivity with SQLAlchemy
- CRUD operations for clothing items
- Image file management
- Data loading utilities

Usage:
    from green_fashion.database import MongoDBManager, SQLConnector

    # MongoDB usage
    wm = MongoDBManager()
    items = wm.get_all_items()

    # SQL usage
    sql_conn = SQLConnector()
    if sql_conn.test_connection():
        results = sql_conn.execute_query("SELECT * FROM items")
"""

from .data_loader import DataLoader
from .mongodb_manager import MongoDBManager
from .sql_connector import SQLConnector, get_sql_connector

__all__ = ["MongoDBManager", "DataLoader", "SQLConnector", "get_sql_connector"]
