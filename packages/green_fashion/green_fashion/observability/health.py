"""
Health check and monitoring endpoints for Green Fashion platform
"""

import asyncio
import time
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class HealthStatus(str, Enum):
    """Health check status enumeration."""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


class HealthCheck(BaseModel):
    """Individual health check result."""

    name: str
    status: HealthStatus
    message: Optional[str] = None
    duration_ms: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ServiceHealth(BaseModel):
    """Overall service health status."""

    service_name: str
    status: HealthStatus
    version: str
    environment: str
    checks: List[HealthCheck]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    uptime_seconds: float


class HealthCheckProvider(ABC):
    """Abstract base class for health check providers."""

    @abstractmethod
    async def check_health(self) -> HealthCheck:
        """Perform health check and return result."""
        pass


class DatabaseHealthCheck(HealthCheckProvider):
    """Health check for database connectivity."""

    def __init__(self, db_manager: Any, name: str = "database"):
        self.db_manager = db_manager
        self.name = name

    async def check_health(self) -> HealthCheck:
        """Check database connectivity."""
        start_time = time.time()

        try:
            # Try to ping the database
            await self.db_manager.ping()
            duration_ms = (time.time() - start_time) * 1000

            return HealthCheck(
                name=self.name,
                status=HealthStatus.HEALTHY,
                message="Database connection successful",
                duration_ms=duration_ms,
                metadata={
                    "connection_pool_size": getattr(
                        self.db_manager, "pool_size", "unknown"
                    )
                },
            )
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return HealthCheck(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Database connection failed: {str(e)}",
                duration_ms=duration_ms,
                metadata={"error": str(e)},
            )


class StorageHealthCheck(HealthCheckProvider):
    """Health check for storage service connectivity."""

    def __init__(self, storage_service: Any, name: str = "storage"):
        self.storage_service = storage_service
        self.name = name

    async def check_health(self) -> HealthCheck:
        """Check storage service connectivity."""
        start_time = time.time()

        try:
            # Try to access storage service
            buckets = await self.storage_service.list_buckets()
            duration_ms = (time.time() - start_time) * 1000

            return HealthCheck(
                name=self.name,
                status=HealthStatus.HEALTHY,
                message="Storage service accessible",
                duration_ms=duration_ms,
                metadata={"bucket_count": len(buckets) if buckets else 0},
            )
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return HealthCheck(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Storage service unavailable: {str(e)}",
                duration_ms=duration_ms,
                metadata={"error": str(e)},
            )


class ModelHealthCheck(HealthCheckProvider):
    """Health check for ML model availability."""

    def __init__(self, model_name: str, model_loader: Any, name: Optional[str] = None):
        self.model_name = model_name
        self.model_loader = model_loader
        self.name = name or f"model_{model_name}"

    async def check_health(self) -> HealthCheck:
        """Check model availability and perform basic inference test."""
        start_time = time.time()

        try:
            # Check if model is loaded
            model = await self.model_loader.get_model(self.model_name)
            if model is None:
                raise Exception(f"Model {self.model_name} not loaded")

            # Perform a basic inference test if supported
            if hasattr(model, "health_check"):
                await model.health_check()

            duration_ms = (time.time() - start_time) * 1000

            return HealthCheck(
                name=self.name,
                status=HealthStatus.HEALTHY,
                message="Model loaded and responsive",
                duration_ms=duration_ms,
                metadata={
                    "model_name": self.model_name,
                    "model_version": getattr(model, "version", "unknown"),
                },
            )
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return HealthCheck(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Model check failed: {str(e)}",
                duration_ms=duration_ms,
                metadata={"error": str(e), "model_name": self.model_name},
            )


class ExternalServiceHealthCheck(HealthCheckProvider):
    """Health check for external service dependencies."""

    def __init__(self, service_url: str, service_name: str, timeout: float = 5.0):
        self.service_url = service_url
        self.service_name = service_name
        self.timeout = timeout

    async def check_health(self) -> HealthCheck:
        """Check external service availability."""
        start_time = time.time()

        try:
            import aiohttp

            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as session:
                async with session.get(f"{self.service_url}/health") as response:
                    duration_ms = (time.time() - start_time) * 1000

                    if response.status == 200:
                        return HealthCheck(
                            name=self.service_name,
                            status=HealthStatus.HEALTHY,
                            message="External service responsive",
                            duration_ms=duration_ms,
                            metadata={
                                "status_code": response.status,
                                "url": self.service_url,
                            },
                        )
                    else:
                        return HealthCheck(
                            name=self.service_name,
                            status=HealthStatus.DEGRADED,
                            message=f"External service returned status {response.status}",
                            duration_ms=duration_ms,
                            metadata={
                                "status_code": response.status,
                                "url": self.service_url,
                            },
                        )
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return HealthCheck(
                name=self.service_name,
                status=HealthStatus.UNHEALTHY,
                message=f"External service unavailable: {str(e)}",
                duration_ms=duration_ms,
                metadata={"error": str(e), "url": self.service_url},
            )


class HealthChecker:
    """Main health checker that aggregates multiple health checks."""

    def __init__(
        self, service_name: str, service_version: str, environment: str = "development"
    ):
        self.service_name = service_name
        self.service_version = service_version
        self.environment = environment
        self.providers: List[HealthCheckProvider] = []
        self.start_time = time.time()

    def add_check(self, provider: HealthCheckProvider) -> None:
        """Add a health check provider."""
        self.providers.append(provider)

    def add_database_check(self, db_manager: Any, name: str = "database") -> None:
        """Add database health check."""
        self.add_check(DatabaseHealthCheck(db_manager, name))

    def add_storage_check(self, storage_service: Any, name: str = "storage") -> None:
        """Add storage health check."""
        self.add_check(StorageHealthCheck(storage_service, name))

    def add_model_check(
        self, model_name: str, model_loader: Any, name: Optional[str] = None
    ) -> None:
        """Add model health check."""
        self.add_check(ModelHealthCheck(model_name, model_loader, name))

    def add_external_service_check(
        self, service_url: str, service_name: str, timeout: float = 5.0
    ) -> None:
        """Add external service health check."""
        self.add_check(ExternalServiceHealthCheck(service_url, service_name, timeout))

    async def check_health(self) -> ServiceHealth:
        """Run all health checks and return aggregated results."""
        # Run all health checks concurrently
        if self.providers:
            checks = await asyncio.gather(
                *[provider.check_health() for provider in self.providers],
                return_exceptions=True,
            )

            # Handle any exceptions that occurred during checks
            health_checks = []
            for i, result in enumerate(checks):
                if isinstance(result, Exception):
                    health_checks.append(
                        HealthCheck(
                            name=f"check_{i}",
                            status=HealthStatus.UNHEALTHY,
                            message=f"Health check failed: {str(result)}",
                            metadata={"error": str(result)},
                        )
                    )
                else:
                    health_checks.append(result)
        else:
            health_checks = []

        # Determine overall service status
        if not health_checks:
            overall_status = HealthStatus.HEALTHY
        elif all(check.status == HealthStatus.HEALTHY for check in health_checks):
            overall_status = HealthStatus.HEALTHY
        elif any(check.status == HealthStatus.UNHEALTHY for check in health_checks):
            overall_status = HealthStatus.UNHEALTHY
        else:
            overall_status = HealthStatus.DEGRADED

        return ServiceHealth(
            service_name=self.service_name,
            status=overall_status,
            version=self.service_version,
            environment=self.environment,
            checks=health_checks,
            uptime_seconds=time.time() - self.start_time,
        )

    async def is_healthy(self) -> bool:
        """Quick health check that returns boolean."""
        health = await self.check_health()
        return health.status == HealthStatus.HEALTHY

    def create_fastapi_endpoints(self, app: Any) -> None:
        """Create FastAPI health check endpoints."""
        from .metrics import get_metrics_collector

        @app.get("/health", response_model=ServiceHealth)
        async def health_check():
            """Health check endpoint."""
            return await self.check_health()

        @app.get("/health/ready")
        async def readiness_check():
            """Readiness check endpoint."""
            health = await self.check_health()
            if health.status == HealthStatus.HEALTHY:
                return {"status": "ready"}
            else:
                return {"status": "not ready", "reason": "health checks failed"}, 503

        @app.get("/health/live")
        async def liveness_check():
            """Liveness check endpoint."""
            # Simple liveness check - just return 200 if service is running
            return {"status": "alive", "timestamp": datetime.now(timezone.utc)}

        @app.get("/metrics")
        async def metrics_endpoint():
            """Prometheus metrics endpoint."""
            collector = get_metrics_collector(self.service_name)
            return collector.get_metrics(), {
                "content-type": collector.get_content_type()
            }
