"""
Usage examples for Green Fashion observability
"""

import asyncio
from fastapi import FastAPI

from .config import ObservabilityConfig
from .logger import configure_logging, get_logger, set_correlation_id
from .metrics import get_metrics_collector, timed_operation
from .tracing import configure_tracing, configure_fastapi_tracing, trace_function
from .health import HealthChecker


# Example 1: Basic setup for a FastAPI application
def setup_observability_for_fastapi(
    app: FastAPI, config: ObservabilityConfig = None
) -> HealthChecker:
    """
    Set up complete observability for a FastAPI application.

    Args:
        app: FastAPI application instance
        config: Observability configuration

    Returns:
        HealthChecker instance
    """
    if config is None:
        config = ObservabilityConfig.from_env()

    # Configure logging
    if config.logging:
        configure_logging(
            level=config.logging.level,
            format_type=config.logging.format_type,
            service_name=config.logging.service_name,
            service_version=config.logging.service_version,
            environment=config.logging.environment,
        )

    # Configure tracing
    if config.tracing and config.tracing.enabled:
        configure_tracing(
            service_name=config.tracing.service_name,
            service_version=config.tracing.service_version,
            jaeger_endpoint=config.tracing.jaeger_endpoint,
            environment=config.tracing.environment,
        )
        configure_fastapi_tracing(app)

    # Configure metrics
    if config.metrics and config.metrics.enabled:
        metrics_collector = get_metrics_collector(config.metrics.service_name)
        metrics_collector.set_service_info(
            version=config.metrics.service_version,
            environment=config.metrics.environment,
        )

    # Configure health checks
    health_checker = None
    if config.health and config.health.enabled:
        health_checker = HealthChecker(
            service_name=config.health.service_name,
            service_version=config.health.service_version,
            environment=config.health.environment,
        )
        health_checker.create_fastapi_endpoints(app)

    return health_checker


# Example 2: Using structured logging
def example_logging():
    """Example of using structured logging."""
    # Configure logging
    configure_logging(
        level="INFO",
        format_type="console",  # Use console format for development
        service_name="example-service",
        environment="development",
    )

    # Get logger
    logger = get_logger(__name__)

    # Log with correlation ID
    set_correlation_id("req-123-456")

    # Structured logging
    logger.info("User logged in", user_id="user123", ip="192.168.1.1")
    logger.warning("High memory usage", memory_percent=85.2, threshold=80)
    logger.error(
        "Database connection failed",
        error="Connection timeout",
        database="users",
        retry_count=3,
    )


# Example 3: Using metrics
@timed_operation("request_duration", method="POST", endpoint="/api/items")
def example_api_endpoint():
    """Example API endpoint with metrics."""
    metrics = get_metrics_collector()

    # Record business metric
    metrics.record_item_added(category="shirt", user_id="user123")

    # Simulate some work
    import time

    time.sleep(0.1)

    return {"status": "success"}


# Example 4: Using tracing
@trace_function("process_image", attributes={"component": "image_processor"})
def process_image(image_path: str) -> dict:
    """Example image processing function with tracing."""
    logger = get_logger(__name__)

    logger.info("Starting image processing", image_path=image_path)

    # Simulate image processing
    import time

    time.sleep(0.5)

    logger.info("Image processing completed", image_path=image_path, result="success")

    return {"processed": True, "path": image_path}


# Example 5: Database operations with observability
class DatabaseExample:
    """Example database class with observability."""

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        self.metrics = get_metrics_collector()

    @trace_function("db_insert")
    async def insert_item(self, item_data: dict) -> str:
        """Insert item with full observability."""
        import time

        start_time = time.time()

        try:
            # Simulate database insert
            await asyncio.sleep(0.1)

            # Record success metrics
            duration = time.time() - start_time
            self.metrics.record_db_operation(
                operation="insert",
                collection="items",
                status="success",
                duration=duration,
            )

            self.logger.info(
                "Item inserted successfully",
                item_id="item123",
                duration_ms=duration * 1000,
            )

            return "item123"

        except Exception as e:
            # Record error metrics
            duration = time.time() - start_time
            self.metrics.record_db_operation(
                operation="insert",
                collection="items",
                status="error",
                duration=duration,
            )

            self.logger.error(
                "Failed to insert item", error=str(e), duration_ms=duration * 1000
            )
            raise


# Example 6: ML model with observability
class ModelExample:
    """Example ML model class with observability."""

    def __init__(self, model_name: str = "clothing_classifier"):
        self.model_name = model_name
        self.logger = get_logger(self.__class__.__name__)
        self.metrics = get_metrics_collector()

    @trace_function("model_predict")
    async def predict(self, image_data: bytes) -> dict:
        """Predict with full observability."""
        import time

        start_time = time.time()

        try:
            # Simulate model inference
            await asyncio.sleep(0.2)

            # Record prediction metrics
            duration = time.time() - start_time
            self.metrics.record_model_prediction(
                model_name=self.model_name,
                model_version="v1.0",
                prediction_type="classification",
                duration=duration,
            )

            prediction = {"category": "shirt", "confidence": 0.95}

            self.logger.info(
                "Model prediction completed",
                model_name=self.model_name,
                prediction=prediction["category"],
                confidence=prediction["confidence"],
                duration_ms=duration * 1000,
            )

            return prediction

        except Exception as e:
            duration = time.time() - start_time

            self.logger.error(
                "Model prediction failed",
                model_name=self.model_name,
                error=str(e),
                duration_ms=duration * 1000,
            )
            raise


# Example 7: Complete health check setup
async def setup_health_checks() -> HealthChecker:
    """Example of setting up comprehensive health checks."""
    health_checker = HealthChecker(
        service_name="green-fashion-api",
        service_version="1.0.0",
        environment="production",
    )

    # Add database health check
    # health_checker.add_database_check(db_manager, "mongodb")

    # Add storage health check
    # health_checker.add_storage_check(storage_service, "gcs")

    # Add model health check
    # health_checker.add_model_check("clothing_classifier", model_loader)

    # Add external service health check
    health_checker.add_external_service_check(
        "https://api.external-service.com", "external_api"
    )

    # Test health check
    health_status = await health_checker.check_health()
    print(f"Service health: {health_status.status}")

    return health_checker


if __name__ == "__main__":
    # Run examples
    print("1. Testing logging...")
    example_logging()

    print("\n2. Testing metrics...")
    example_api_endpoint()

    print("\n3. Testing tracing...")
    result = process_image("/path/to/image.jpg")
    print(f"Processing result: {result}")

    print("\n4. Testing async database operations...")
    asyncio.run(DatabaseExample().insert_item({"name": "Blue Shirt"}))

    print("\n5. Testing ML model...")
    asyncio.run(ModelExample().predict(b"fake_image_data"))

    print("\n6. Testing health checks...")
    asyncio.run(setup_health_checks())
