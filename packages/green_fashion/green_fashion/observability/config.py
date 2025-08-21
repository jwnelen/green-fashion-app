"""
Configuration for Green Fashion observability
"""

from typing import Optional
from pydantic import BaseModel, Field


class LoggingConfig(BaseModel):
    """Logging configuration."""

    level: str = Field(default="INFO", description="Log level")
    format_type: str = Field(default="json", description="Log format (json or console)")
    service_name: str = Field(default="green-fashion", description="Service name")
    service_version: str = Field(default="0.1.0", description="Service version")
    environment: str = Field(default="development", description="Environment")


class TracingConfig(BaseModel):
    """Tracing configuration."""

    enabled: bool = Field(default=True, description="Enable tracing")
    service_name: str = Field(default="green-fashion", description="Service name")
    service_version: str = Field(default="0.1.0", description="Service version")
    jaeger_endpoint: str = Field(
        default="http://localhost:14268/api/traces",
        description="Jaeger collector endpoint",
    )
    environment: str = Field(default="development", description="Environment")


class MetricsConfig(BaseModel):
    """Metrics configuration."""

    enabled: bool = Field(default=True, description="Enable metrics collection")
    service_name: str = Field(default="green-fashion", description="Service name")
    service_version: str = Field(default="0.1.0", description="Service version")
    environment: str = Field(default="development", description="Environment")


class HealthConfig(BaseModel):
    """Health check configuration."""

    enabled: bool = Field(default=True, description="Enable health checks")
    service_name: str = Field(default="green-fashion", description="Service name")
    service_version: str = Field(default="0.1.0", description="Service version")
    environment: str = Field(default="development", description="Environment")


class ObservabilityConfig(BaseModel):
    """Complete observability configuration."""

    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    tracing: TracingConfig = Field(default_factory=TracingConfig)
    metrics: MetricsConfig = Field(default_factory=MetricsConfig)
    health: HealthConfig = Field(default_factory=HealthConfig)

    @classmethod
    def from_env(cls, env_prefix: str = "GREEN_FASHION_") -> "ObservabilityConfig":
        """Create configuration from environment variables."""
        import os

        def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
            return os.getenv(f"{env_prefix}{key}", default)

        # Get common values
        service_name = get_env("SERVICE_NAME", "green-fashion")
        service_version = get_env("SERVICE_VERSION", "0.1.0")
        environment = get_env("ENVIRONMENT", "development")

        return cls(
            logging=LoggingConfig(
                level=get_env("LOG_LEVEL", "INFO"),
                format_type=get_env("LOG_FORMAT", "json"),
                service_name=service_name,
                service_version=service_version,
                environment=environment,
            ),
            tracing=TracingConfig(
                enabled=get_env("TRACING_ENABLED", "true").lower() == "true",
                service_name=service_name,
                service_version=service_version,
                jaeger_endpoint=get_env(
                    "JAEGER_ENDPOINT", "http://localhost:14268/api/traces"
                ),
                environment=environment,
            ),
            metrics=MetricsConfig(
                enabled=get_env("METRICS_ENABLED", "true").lower() == "true",
                service_name=service_name,
                service_version=service_version,
                environment=environment,
            ),
            health=HealthConfig(
                enabled=get_env("HEALTH_ENABLED", "true").lower() == "true",
                service_name=service_name,
                service_version=service_version,
                environment=environment,
            ),
        )
