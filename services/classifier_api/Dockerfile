# Multi-stage build for Green Fashion Classifier API
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

# Set working directory to mimic project structure
WORKDIR /project/services/classifier_api

# Copy packages directory to project root
COPY packages/ /project/packages/

# Copy dependency files
COPY services/classifier_api/pyproject.toml services/classifier_api/uv.lock ./

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

# Set working directory to mimic project structure
WORKDIR /project/services/classifier_api

# Copy Python virtual environment from builder stage
COPY --from=builder --chown=app:app /project/services/classifier_api/.venv ./.venv

# Copy packages directory to project root
COPY --chown=app:app packages/ /project/packages/

# Copy application code
COPY --chown=app:app services/classifier_api/src/ ./src/

# Create cache directories with proper ownership
RUN mkdir -p /project/.cache/torch /project/.cache/huggingface && \
    chown -R app:app /project/.cache

# Switch to non-root user
USER app

# Set environment variables
ENV PYTHONPATH=/project
ENV PATH="/project/services/classifier_api/.venv/bin:$PATH"
ENV PORT=8001
ENV TORCH_HOME=/project/.cache/torch
ENV HF_HOME=/project/.cache/huggingface
ENV TRANSFORMERS_CACHE=/project/.cache/huggingface

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Expose port
EXPOSE ${PORT}

# Start command
CMD ["sh", "-c", "python -m uvicorn src.main:app --host 0.0.0.0 --port ${PORT}"]
