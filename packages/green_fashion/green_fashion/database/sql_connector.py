"""
SQL Connector module for Green Fashion project.

This module provides SQL database connectivity using SQLAlchemy ORM.
Supports MySQL and other SQL databases for the Green Fashion application.
"""

import os
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

from loguru import logger
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker


class SQLConnector:
    """
    SQL database connector using SQLAlchemy.

    Provides connection management and basic database operations
    for the Green Fashion application.
    """

    def __init__(self, connection_string: Optional[str] = None):
        """
        Initialize the SQL connector.

        Args:
            connection_string: Database connection string. If None, will try to get from environment.
        """
        self.connection_string = connection_string or self._get_connection_string()
        self.engine = None
        self.SessionLocal = None
        self._initialize_engine()

    def _get_connection_string(self) -> str:
        """
        Get database connection string from environment variables.

        Returns:
            Database connection string

        Raises:
            ValueError: If connection string cannot be determined
        """
        # Try to get from various environment variable names
        connection_string = (
            os.getenv("MYSQL_CONNECTION_STRING")
            or os.getenv("DATABASE_URL")
            or os.getenv("DB_CONNECTION_STRING")
        )

        if connection_string:
            return connection_string

        # Try to build from individual components
        host = os.getenv("DB_HOST", "localhost")
        port = int(os.getenv("DB_PORT", "3306"))
        username = os.getenv("DB_USERNAME") or os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")
        database = os.getenv("DB_NAME") or os.getenv("DATABASE_NAME")

        if not all([username, password, database]):
            raise ValueError(
                "Database connection string not found. Please provide either "
                "MYSQL_CONNECTION_STRING environment variable or "
                "DB_HOST, DB_USERNAME, DB_PASSWORD, and DB_NAME"
            )

        # Build MySQL connection string with PyMySQL driver
        return f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"

    def _initialize_engine(self):
        """Initialize SQLAlchemy engine and session factory."""
        try:
            self.engine = create_engine(
                self.connection_string,
                echo=False,  # Set to True for SQL query logging
                pool_pre_ping=True,  # Verify connections before use
                pool_recycle=3600,  # Recycle connections every hour
            )
            self.SessionLocal = sessionmaker(
                autocommit=False, autoflush=False, bind=self.engine
            )
            logger.info("SQL connector initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize SQL connector: {e}")
            raise

    @contextmanager
    def get_session(self):
        """
        Context manager for database sessions.

        Yields:
            SQLAlchemy session object
        """
        session = self.SessionLocal()
        try:
            yield session
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()

    def test_connection(self) -> bool:
        """
        Test database connection.

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False

    def execute_query(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a raw SQL query and return results.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            List of dictionaries representing query results
        """
        try:
            with self.get_session() as session:
                result = session.execute(text(query), params or {})

                # Convert result to list of dictionaries
                if result.returns_rows:
                    columns = result.keys()
                    return [dict(zip(columns, row)) for row in result.fetchall()]
                else:
                    session.commit()
                    return []
        except SQLAlchemyError as e:
            logger.error(f"Query execution failed: {e}")
            raise

    def execute_many(self, query: str, params_list: List[Dict[str, Any]]) -> None:
        """
        Execute a query multiple times with different parameters.

        Args:
            query: SQL query string
            params_list: List of parameter dictionaries
        """
        try:
            with self.get_session() as session:
                for params in params_list:
                    session.execute(text(query), params)
                session.commit()
            logger.info(f"Executed query {len(params_list)} times successfully")
        except SQLAlchemyError as e:
            logger.error(f"Batch query execution failed: {e}")
            raise

    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Get information about a table's structure.

        Args:
            table_name: Name of the table

        Returns:
            List of column information dictionaries
        """
        query = """
        SELECT
            COLUMN_NAME,
            DATA_TYPE,
            IS_NULLABLE,
            COLUMN_DEFAULT,
            COLUMN_KEY,
            EXTRA
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = :table_name
        ORDER BY ORDINAL_POSITION
        """

        return self.execute_query(query, {"table_name": table_name})

    def list_tables(self) -> List[str]:
        """
        List all tables in the current database.

        Returns:
            List of table names
        """
        query = """
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = DATABASE()
        ORDER BY TABLE_NAME
        """

        result = self.execute_query(query)
        return [row["TABLE_NAME"] for row in result]

    def close(self):
        """Close the database engine and all connections."""
        if self.engine:
            self.engine.dispose()
            logger.info("SQL connector closed")


# Convenience function to create a connector instance
def get_sql_connector(connection_string: Optional[str] = None) -> SQLConnector:
    """
    Create and return a SQL connector instance.

    Args:
        connection_string: Optional database connection string

    Returns:
        SQLConnector instance
    """
    return SQLConnector(connection_string)
