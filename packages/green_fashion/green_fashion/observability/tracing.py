"""
Distributed tracing for Green Fashion platform using OpenTelemetry
"""

import functools
from typing import Any, Callable, Dict, Optional, TypeVar

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.pymongo import PymongoInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource

F = TypeVar("F", bound=Callable[..., Any])

# Global tracer instance
_tracer: Optional[trace.Tracer] = None


def configure_tracing(
    service_name: str = "green-fashion",
    service_version: str = "0.1.0",
    jaeger_endpoint: str = "http://localhost:14268/api/traces",
    environment: str = "development",
) -> None:
    """
    Configure distributed tracing with OpenTelemetry and Jaeger.

    Args:
        service_name: Name of the service
        service_version: Version of the service
        jaeger_endpoint: Jaeger collector endpoint
        environment: Environment (development, staging, production)
    """
    # Create resource with service information
    resource = Resource.create(
        {
            SERVICE_NAME: service_name,
            SERVICE_VERSION: service_version,
            "environment": environment,
        }
    )

    # Set up tracer provider
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    # Configure Jaeger exporter
    jaeger_exporter = JaegerExporter(
        endpoint=jaeger_endpoint,
    )

    # Add span processor
    span_processor = BatchSpanProcessor(jaeger_exporter)
    provider.add_span_processor(span_processor)

    # Auto-instrument common libraries
    RequestsInstrumentor().instrument()
    PymongoInstrumentor().instrument()


def configure_fastapi_tracing(app: Any) -> None:
    """Configure tracing for FastAPI application."""
    FastAPIInstrumentor.instrument_app(app)


def get_tracer(name: str = "green-fashion") -> trace.Tracer:
    """
    Get a tracer instance.

    Args:
        name: Tracer name

    Returns:
        OpenTelemetry tracer
    """
    return trace.get_tracer(name)


def trace_function(
    operation_name: Optional[str] = None, attributes: Optional[Dict[str, Any]] = None
) -> Callable[[F], F]:
    """
    Decorator to trace function execution.

    Args:
        operation_name: Name of the operation (defaults to function name)
        attributes: Additional attributes to add to the span

    Returns:
        Decorated function
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            tracer = get_tracer()
            span_name = operation_name or f"{func.__module__}.{func.__name__}"

            with tracer.start_as_current_span(span_name) as span:
                # Add function attributes
                span.set_attribute("function.name", func.__name__)
                span.set_attribute("function.module", func.__module__)

                # Add custom attributes
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, value)

                try:
                    result = func(*args, **kwargs)
                    span.set_attribute("function.result", "success")
                    return result
                except Exception as e:
                    span.set_attribute("function.result", "error")
                    span.set_attribute("error.type", type(e).__name__)
                    span.set_attribute("error.message", str(e))
                    span.record_exception(e)
                    raise

        return wrapper

    return decorator


class TracingMixin:
    """Mixin class to add tracing capabilities to any class."""

    @property
    def tracer(self) -> trace.Tracer:
        """Get tracer for this class."""
        return get_tracer(f"{self.__class__.__module__}.{self.__class__.__name__}")

    def start_span(self, operation_name: str, **attributes: Any) -> trace.Span:
        """Start a new span for this class."""
        span = self.tracer.start_span(operation_name)

        # Add class information
        span.set_attribute("class.name", self.__class__.__name__)
        span.set_attribute("class.module", self.__class__.__module__)

        # Add custom attributes
        for key, value in attributes.items():
            span.set_attribute(key, value)

        return span


def trace_database_operation(operation: str, collection: str) -> Callable[[F], F]:
    """
    Decorator specifically for database operations.

    Args:
        operation: Database operation (insert, find, update, delete)
        collection: Database collection name

    Returns:
        Decorated function
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            tracer = get_tracer()
            span_name = f"db.{operation}.{collection}"

            with tracer.start_as_current_span(span_name) as span:
                span.set_attribute("db.operation", operation)
                span.set_attribute("db.collection", collection)
                span.set_attribute("db.system", "mongodb")

                try:
                    result = func(*args, **kwargs)
                    span.set_attribute("db.result", "success")
                    return result
                except Exception as e:
                    span.set_attribute("db.result", "error")
                    span.set_attribute("error.type", type(e).__name__)
                    span.set_attribute("error.message", str(e))
                    span.record_exception(e)
                    raise

        return wrapper

    return decorator


def trace_model_inference(
    model_name: str, model_version: str = "latest"
) -> Callable[[F], F]:
    """
    Decorator specifically for ML model inference.

    Args:
        model_name: Name of the ML model
        model_version: Version of the ML model

    Returns:
        Decorated function
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            tracer = get_tracer()
            span_name = f"ml.inference.{model_name}"

            with tracer.start_as_current_span(span_name) as span:
                span.set_attribute("ml.model.name", model_name)
                span.set_attribute("ml.model.version", model_version)
                span.set_attribute("ml.operation", "inference")

                try:
                    result = func(*args, **kwargs)
                    span.set_attribute("ml.result", "success")
                    return result
                except Exception as e:
                    span.set_attribute("ml.result", "error")
                    span.set_attribute("error.type", type(e).__name__)
                    span.set_attribute("error.message", str(e))
                    span.record_exception(e)
                    raise

        return wrapper

    return decorator


def trace_storage_operation(operation: str, bucket: str) -> Callable[[F], F]:
    """
    Decorator specifically for storage operations.

    Args:
        operation: Storage operation (upload, download, delete)
        bucket: Storage bucket name

    Returns:
        Decorated function
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            tracer = get_tracer()
            span_name = f"storage.{operation}.{bucket}"

            with tracer.start_as_current_span(span_name) as span:
                span.set_attribute("storage.operation", operation)
                span.set_attribute("storage.bucket", bucket)
                span.set_attribute("storage.system", "gcs")

                try:
                    result = func(*args, **kwargs)
                    span.set_attribute("storage.result", "success")
                    return result
                except Exception as e:
                    span.set_attribute("storage.result", "error")
                    span.set_attribute("error.type", type(e).__name__)
                    span.set_attribute("error.message", str(e))
                    span.record_exception(e)
                    raise

        return wrapper

    return decorator
