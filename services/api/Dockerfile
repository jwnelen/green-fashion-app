# Multi-stage build for Green Fashion API
FROM python:3.13-slim as builder

# Set build arguments
ARG DEBIAN_FRONTEND=noninteractive

# Install system dependencies needed for building
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app

# Set working directory
WORKDIR /app

# Create directory structure for local dependencies
RUN mkdir -p ../packages
COPY packages/ ../packages/

# Copy dependency files
COPY services/api/pyproject.toml services/api/uv.lock ./

# Install Python dependencies using uv
RUN uv sync --frozen --no-dev

# Production stage
FROM python:3.13-slim

# Install runtime dependencies and curl for health checks
RUN apt-get update && apt-get install -y \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash --uid 1000 app

# Set working directory
WORKDIR /app

# Copy Python virtual environment from builder stage
COPY --from=builder --chown=app:app /app/.venv /app/.venv

# Create directory structure for local dependencies
RUN mkdir -p ../packages
COPY --chown=app:app packages/ ../packages/

# Copy application code
COPY --chown=app:app services/api/src/ ./src/

# Switch to non-root user
USER app

# Set environment variables
ENV PYTHONPATH=/app
ENV PATH="/app/.venv/bin:$PATH"
ENV PORT=8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Expose port
EXPOSE ${PORT}

# Start command
CMD ["sh", "-c", "python -m uvicorn src.main:app --host 0.0.0.0 --port ${PORT}"]
