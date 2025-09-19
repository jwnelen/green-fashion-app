import os
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

from loguru import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


# ---------- Helpers ----------
def _build_traditional_mysql_url_from_env() -> str:
    """
    Build a MySQL connection URL from env vars, e.g.:
      DB_HOST, DB_PORT, DB_USERNAME/DB_USER, DB_PASSWORD, DB_NAME.
    Returns a PyMySQL URL for the sync engine.
    """
    host = os.getenv("DB_HOST", "localhost")
    port = int(os.getenv("DB_PORT", "3306"))
    username = os.getenv("DB_USERNAME") or os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    database = os.getenv("DB_NAME") or os.getenv("DATABASE_NAME")

    if not all([username, password, database]):
        raise ValueError(
            "Database connection string not found. Provide either "
            "MYSQL_CONNECTION_STRING / DATABASE_URL / DB_CONNECTION_STRING, or "
            "DB_HOST, DB_USERNAME/DB_USER, DB_PASSWORD, DB_NAME"
        )

    # Sync (PyMySQL) URL
    return f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"


def _resolve_sync_connection_string(explicit: Optional[str]) -> str:
    """
    Resolve the sync (sqlalchemy) connection URL:
      1) explicit arg if provided
      2) env vars MYSQL_CONNECTION_STRING / DATABASE_URL / DB_CONNECTION_STRING
      3) Cloud SQL Unix socket, if present
      4) traditional host/port/user/pass
    """
    if explicit:
        return explicit

    # Direct env URL?
    env_url = (
        os.getenv("MYSQL_CONNECTION_STRING")
        or os.getenv("DATABASE_URL")
        or os.getenv("DB_CONNECTION_STRING")
    )
    if env_url:
        return env_url

    # Cloud SQL via Unix socket
    cloudsql_path = "/cloudsql"
    instance_connection_name = os.getenv("INSTANCE_CONNECTION_NAME")
    if os.path.exists(cloudsql_path) and instance_connection_name:
        username = os.getenv("DB_USER") or os.getenv("DB_USERNAME")
        password = os.getenv("DB_PASS") or os.getenv("DB_PASSWORD")
        database = os.getenv("DB_NAME")
        if not all([username, password, database]):
            raise ValueError(
                "Missing Cloud SQL env vars: DB_USER/DB_USERNAME, DB_PASS/DB_PASSWORD, DB_NAME"
            )
        socket_path = f"{cloudsql_path}/{instance_connection_name}"
        # Sync (PyMySQL) URL over Unix socket
        return f"mysql+pymysql://{username}:{password}@/{database}?unix_socket={socket_path}"

    # Traditional
    return _build_traditional_mysql_url_from_env()


def _resolve_async_connection_string(explicit: Optional[str]) -> str:
    """
    Resolve the async (sqlalchemy) connection URL, mirroring the sync logic
    but using aiomysql where appropriate.
    """
    if explicit:
        # If caller passed a URL that already uses an async dialect, trust it.
        if explicit.startswith("mysql+aiomysql://"):
            return explicit
        # Convert common sync URLs to async aiomysql for MySQL.
        if explicit.startswith("mysql+pymysql://"):
            return explicit.replace("mysql+pymysql://", "mysql+aiomysql://", 1)
        if explicit.startswith("mysql://"):
            return explicit.replace("mysql://", "mysql+aiomysql://", 1)
        # Otherwise return as-is (may be another async dialect).
        return explicit

    env_url = (
        os.getenv("MYSQL_CONNECTION_STRING")
        or os.getenv("DATABASE_URL")
        or os.getenv("DB_CONNECTION_STRING")
    )
    if env_url:
        if env_url.startswith("mysql+aiomysql://"):
            return env_url
        if env_url.startswith("mysql+pymysql://"):
            return env_url.replace("mysql+pymysql://", "mysql+aiomysql://", 1)
        if env_url.startswith("mysql://"):
            return env_url.replace("mysql://", "mysql+aiomysql://", 1)
        # Allow non-MySQL URLs (e.g., asyncpg) to pass through unchanged
        return env_url

    cloudsql_path = "/cloudsql"
    instance_connection_name = os.getenv("INSTANCE_CONNECTION_NAME")
    if os.path.exists(cloudsql_path) and instance_connection_name:
        username = os.getenv("DB_USER") or os.getenv("DB_USERNAME")
        password = os.getenv("DB_PASS") or os.getenv("DB_PASSWORD")
        database = os.getenv("DB_NAME")
        if not all([username, password, database]):
            raise ValueError(
                "Missing Cloud SQL env vars: DB_USER/DB_USERNAME, DB_PASS/DB_PASSWORD, DB_NAME"
            )
        socket_path = f"{cloudsql_path}/{instance_connection_name}"
        # Async (aiomysql) URL over Unix socket
        return f"mysql+aiomysql://{username}:{password}@/{database}?unix_socket={socket_path}"

    # Traditional async URL
    sync_url = _build_traditional_mysql_url_from_env()
    return sync_url.replace("mysql+pymysql://", "mysql+aiomysql://", 1)


class AsyncSQLConnector:
    """
    Asynchronous SQL database connector using SQLAlchemy 2.x async API.
    """

    def __init__(self, connection_string: Optional[str] = None):
        self.connection_string = _resolve_async_connection_string(connection_string)
        self.engine = None
        self.SessionLocal = None
        self._initialize_engine()

    def _initialize_engine(self):
        try:
            self.engine = create_async_engine(
                self.connection_string,
                echo=False,
                pool_pre_ping=True,
            )
            self.SessionLocal = async_sessionmaker(
                self.engine,
                expire_on_commit=False,
                class_=AsyncSession,
            )
            logger.info("Async SQL connector initialized")
        except Exception as e:
            logger.error(f"Failed to initialize async SQL connector: {e}")
            raise

    @asynccontextmanager
    async def transaction(self):
        """
        Async transaction context that commits on success and rolls back on error.
        Yields an AsyncSession.
        """
        async with self.SessionLocal() as session:
            try:
                async with session.begin():
                    yield session
            except Exception as e:
                # session.begin() will roll back automatically on exception
                logger.error(f"Async DB transaction error: {e}")
                raise

    async def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None):
        """
        Execute a SQL statement asynchronously. Returns:
          - list[dict] for SELECT (rows)
          - None for non-SELECT
        """
        async with self.transaction() as session:
            result = await session.execute(text(query), params or {})
            if result.returns_rows:
                return [dict(r) for r in result.mappings().all()]
            return None

    async def fetch_one(self, query: str, params: Optional[Dict[str, Any]] = None):
        async with self.transaction() as session:
            result = await session.execute(text(query), params or {})
            row = result.mappings().first()
            return dict(row) if row else None

    async def test_connection(self) -> bool:
        try:
            async with self.transaction() as session:
                await session.execute(text("SELECT 1"))
            logger.info("Async DB connection OK")
            return True
        except Exception as e:
            logger.error(f"Async DB connection failed: {e}")
            return False

    async def list_tables(self) -> List[str]:
        query = """
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = DATABASE()
        ORDER BY TABLE_NAME
        """
        rows = await self.execute_query(query) or []
        return [row["TABLE_NAME"] for row in rows]

    async def close(self):
        if self.engine:
            await self.engine.dispose()
            logger.info("Async SQL connector closed")


def get_async_sql_connector(
    connection_string: Optional[str] = None,
) -> AsyncSQLConnector:
    """Async connector (use this for FastAPI async routes)."""
    return AsyncSQLConnector(connection_string)
