"""
Loguru setup utilities for consistent, structured logging across services.

Usage in services:

    from green_fashion.logging_utils import setup_logging, logger, request_context_middleware

    setup_logging(service_name="api")
    app.middleware("http")(request_context_middleware)

Then use `logger` everywhere:

    logger.info("Starting up")
    logger.bind(user_id=uid).warning("Something odd")
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
import uuid
from contextvars import ContextVar
from typing import Any, Callable

from loguru import logger as _logger

# Context for per-request fields
request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)
user_id_ctx: ContextVar[str | None] = ContextVar("user_id", default=None)


class InterceptHandler(logging.Handler):
    """Redirect stdlib logging records to Loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = _logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find the caller from where logging was called
        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        _logger.bind(request_id=request_id_ctx.get(), user_id=user_id_ctx.get()).opt(
            depth=depth, exception=record.exc_info
        ).log(level, record.getMessage())


def _console_format() -> str:
    # Colorized, concise format for local dev
    return (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> "
        "| <level>{level: <8}</level> "
        "| <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> "
        "| <magenta>{extra[service]}</magenta> "
        "- <level>{message}</level>"
    )


def _serialize(record: dict) -> str:
    # Ensure extras are embedded and include context variables
    payload = dict(record)
    payload["request_id"] = (
        payload.get("extra", {}).get("request_id") or request_id_ctx.get()
    )
    payload["user_id"] = payload.get("extra", {}).get("user_id") or user_id_ctx.get()
    # Remove non-serializable elements
    payload.pop("exception", None)
    return json.dumps(payload, default=str)


def setup_logging(
    *,
    service_name: str = "app",
    level: str | int | None = None,
    json_logs: bool | None = None,
    log_file: str | None = None,
    rotation: str | int | None = None,
    retention: str | int | None = None,
    enqueue: bool | None = None,
) -> None:
    """Configure Loguru and intercept stdlib loggers.

    Honors env vars when parameters are not provided:
      - LOG_LEVEL (default: INFO)
      - LOG_FORMAT ("json" for JSON, else pretty)
      - LOG_FILE (path to log file, optional)
      - LOG_ROTATION (e.g., "10 MB" or "1 week")
      - LOG_RETENTION (e.g., "7 days")
      - LOG_ENQUEUE ("1" to enable multiprocess-safety)
    """

    # Resolve settings with env fallbacks
    level = level or os.getenv("LOG_LEVEL", "INFO")
    json_logs = (
        json_logs
        if json_logs is not None
        else os.getenv("LOG_FORMAT", "").lower() == "json"
    )
    log_file = log_file or os.getenv("LOG_FILE")
    rotation = rotation or os.getenv("LOG_ROTATION", "50 MB")
    retention = retention or os.getenv("LOG_RETENTION", "14 days")
    enqueue = enqueue if enqueue is not None else os.getenv("LOG_ENQUEUE", "0") == "1"

    # Remove default handlers
    _logger.remove()

    # Common extra fields
    base_extra = {"service": service_name}

    # Console / stdout sink
    if json_logs:
        # Emit JSON compatible with GCP Cloud Logging expectations
        def gcp_json_sink(message):
            rec = message.record
            lvl = rec["level"].name
            # Map Loguru levels to GCP severities
            severity_map = {
                "TRACE": "DEBUG",
                "DEBUG": "DEBUG",
                "INFO": "INFO",
                "SUCCESS": "NOTICE",
                "WARNING": "WARNING",
                "ERROR": "ERROR",
                "CRITICAL": "CRITICAL",
            }
            payload = {
                "severity": severity_map.get(lvl, "INFO"),
                "message": rec["message"],
                "service": rec["extra"].get("service"),
                "request_id": rec["extra"].get("request_id"),
                "user_id": rec["extra"].get("user_id"),
                "logger": rec["name"],
                "function": rec["function"],
                "line": rec["line"],
                "time": rec["time"].isoformat(),
            }
            sys.stdout.write(json.dumps(payload) + "\n")

        _logger.add(
            gcp_json_sink,
            level=level,
            backtrace=False,
            diagnose=False,
            enqueue=enqueue,
        )
    else:
        _logger.add(
            sys.stdout,
            level=level,
            format=_console_format(),
            backtrace=False,
            diagnose=False,
            enqueue=enqueue,
        )

    # Optional file sink
    if log_file:
        _logger.add(
            log_file,
            level=level,
            format=None if json_logs else _console_format(),
            serialize=json_logs,
            rotation=rotation,
            retention=retention,
            enqueue=enqueue,
        )

    # Intercept stdlib logging (including uvicorn, fastapi)
    intercept = InterceptHandler()
    logging.basicConfig(handlers=[intercept], level=0, force=True)

    for name in (
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
        "fastapi",
        "asyncio",
        "pymongo",
        "google",
        "PIL",
    ):
        logging.getLogger(name).handlers = [intercept]
        logging.getLogger(name).propagate = False
        logging.getLogger(name).setLevel(
            level
            if isinstance(level, int)
            else logging.getLevelName(str(level).upper())
        )

    # Bind base fields
    _logger.configure(extra=base_extra)


async def request_context_middleware(request, call_next: Callable[[Any], Any]):
    """Starlette/FASTAPI middleware to set request_id and log request/response.

    - Reads `X-Request-ID` if provided, else generates one.
    - Binds context for all logs within the request scope.
    - Logs request method, path, status, and latency.
    """
    rid = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    token = request_id_ctx.set(rid)

    start = time.perf_counter()
    response = None
    try:
        response = await call_next(request)
        return response
    finally:
        duration_ms = (time.perf_counter() - start) * 1000
        status_code = getattr(response, "status_code", 500)
        _logger.bind(request_id=rid).info(
            "{method} {path} -> {status} in {duration:.1f}ms",
            method=request.method,
            path=request.url.path,
            status=status_code,
            duration=duration_ms,
        )
        if response is not None:
            response.headers["X-Request-ID"] = rid
        request_id_ctx.reset(token)


# expose a convenient logger symbol
logger = _logger
