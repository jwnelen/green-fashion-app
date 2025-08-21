"""
Metrics collection for Green Fashion platform
"""

import time
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, Generator, Optional, TypeVar

from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    Info,
    CollectorRegistry,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

F = TypeVar("F", bound=Callable[..., Any])


class MetricsCollector:
    """Centralized metrics collection for Green Fashion services."""

    def __init__(
        self,
        service_name: str = "green_fashion",
        registry: Optional[CollectorRegistry] = None,
    ):
        self.service_name = service_name
        self.registry = registry or CollectorRegistry()

        # Service info
        self.service_info = Info(
            "green_fashion_service_info",
            "Green Fashion service information",
            registry=self.registry,
        )

        # Request metrics
        self.request_count = Counter(
            "green_fashion_requests_total",
            "Total number of requests",
            ["method", "endpoint", "status_code", "service"],
            registry=self.registry,
        )

        self.request_duration = Histogram(
            "green_fashion_request_duration_seconds",
            "Request duration in seconds",
            ["method", "endpoint", "service"],
            registry=self.registry,
        )

        # API-specific metrics
        self.api_errors = Counter(
            "green_fashion_api_errors_total",
            "Total API errors",
            ["error_type", "endpoint", "service"],
            registry=self.registry,
        )

        # ML model metrics
        self.model_predictions = Counter(
            "green_fashion_model_predictions_total",
            "Total model predictions",
            ["model_name", "model_version", "prediction_type"],
            registry=self.registry,
        )

        self.model_inference_duration = Histogram(
            "green_fashion_model_inference_duration_seconds",
            "Model inference duration in seconds",
            ["model_name", "model_version"],
            registry=self.registry,
        )

        self.model_accuracy = Gauge(
            "green_fashion_model_accuracy",
            "Model accuracy score",
            ["model_name", "model_version"],
            registry=self.registry,
        )

        # Database metrics
        self.db_operations = Counter(
            "green_fashion_db_operations_total",
            "Total database operations",
            ["operation", "collection", "status"],
            registry=self.registry,
        )

        self.db_operation_duration = Histogram(
            "green_fashion_db_operation_duration_seconds",
            "Database operation duration in seconds",
            ["operation", "collection"],
            registry=self.registry,
        )

        # Storage metrics
        self.storage_operations = Counter(
            "green_fashion_storage_operations_total",
            "Total storage operations",
            ["operation", "bucket", "status"],
            registry=self.registry,
        )

        # Business metrics
        self.items_added = Counter(
            "green_fashion_items_added_total",
            "Total items added to wardrobe",
            ["category", "user_id"],
            registry=self.registry,
        )

        self.outfit_generations = Counter(
            "green_fashion_outfit_generations_total",
            "Total outfit generations",
            ["generation_type", "user_id"],
            registry=self.registry,
        )

    def set_service_info(self, version: str, environment: str, **kwargs: str) -> None:
        """Set service information."""
        info_dict = {
            "version": version,
            "environment": environment,
            "service": self.service_name,
            **kwargs,
        }
        self.service_info.info(info_dict)

    def record_request(
        self, method: str, endpoint: str, status_code: int, duration: float
    ) -> None:
        """Record HTTP request metrics."""
        self.request_count.labels(
            method=method,
            endpoint=endpoint,
            status_code=str(status_code),
            service=self.service_name,
        ).inc()

        self.request_duration.labels(
            method=method, endpoint=endpoint, service=self.service_name
        ).observe(duration)

    def record_api_error(self, error_type: str, endpoint: str) -> None:
        """Record API error."""
        self.api_errors.labels(
            error_type=error_type, endpoint=endpoint, service=self.service_name
        ).inc()

    def record_model_prediction(
        self, model_name: str, model_version: str, prediction_type: str, duration: float
    ) -> None:
        """Record ML model prediction metrics."""
        self.model_predictions.labels(
            model_name=model_name,
            model_version=model_version,
            prediction_type=prediction_type,
        ).inc()

        self.model_inference_duration.labels(
            model_name=model_name, model_version=model_version
        ).observe(duration)

    def set_model_accuracy(
        self, model_name: str, model_version: str, accuracy: float
    ) -> None:
        """Set model accuracy metric."""
        self.model_accuracy.labels(
            model_name=model_name, model_version=model_version
        ).set(accuracy)

    def record_db_operation(
        self, operation: str, collection: str, status: str, duration: float
    ) -> None:
        """Record database operation metrics."""
        self.db_operations.labels(
            operation=operation, collection=collection, status=status
        ).inc()

        self.db_operation_duration.labels(
            operation=operation, collection=collection
        ).observe(duration)

    def record_storage_operation(
        self, operation: str, bucket: str, status: str
    ) -> None:
        """Record storage operation metrics."""
        self.storage_operations.labels(
            operation=operation, bucket=bucket, status=status
        ).inc()

    def record_item_added(self, category: str, user_id: str) -> None:
        """Record item added to wardrobe."""
        self.items_added.labels(category=category, user_id=user_id).inc()

    def record_outfit_generation(self, generation_type: str, user_id: str) -> None:
        """Record outfit generation."""
        self.outfit_generations.labels(
            generation_type=generation_type, user_id=user_id
        ).inc()

    @contextmanager
    def time_operation(
        self, metric: Histogram, **labels: str
    ) -> Generator[None, None, None]:
        """Context manager to time operations."""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            metric.labels(**labels).observe(duration)

    def get_metrics(self) -> str:
        """Get metrics in Prometheus format."""
        return generate_latest(self.registry).decode("utf-8")

    def get_content_type(self) -> str:
        """Get content type for metrics endpoint."""
        return CONTENT_TYPE_LATEST


# Global metrics collector instance
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector(service_name: str = "green_fashion") -> MetricsCollector:
    """Get or create the global metrics collector."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector(service_name)
    return _metrics_collector


def timed_operation(metric_name: str = None, **metric_labels: str) -> Callable[[F], F]:
    """Decorator to time function execution and record metrics."""

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            collector = get_metrics_collector()

            # Use provided metric or create default
            if metric_name and hasattr(collector, metric_name):
                metric = getattr(collector, metric_name)
            else:
                # Default to request_duration if no specific metric provided
                metric = collector.request_duration
                if not metric_labels:
                    metric_labels.update(
                        {
                            "method": "function",
                            "endpoint": func.__name__,
                            "service": collector.service_name,
                        }
                    )

            with collector.time_operation(metric, **metric_labels):
                return func(*args, **kwargs)

        return wrapper

    return decorator
