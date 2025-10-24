# syntax=docker/dockerfile:1

# =============================================================================
# Multi-stage Dockerfile for FastAPI + UV
# Based on UV Docker best practices: https://docs.astral.sh/uv/guides/integration/docker/
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Builder - Install dependencies
# -----------------------------------------------------------------------------
FROM python:3.13-slim-bookworm AS builder

# Install uv from official image (pinned version for reproducibility)
COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Enable bytecode compilation for faster startup
ENV UV_COMPILE_BYTECODE=1

# Copy from /root/.cache/uv to /root/.cache/uv for caching
ENV UV_LINK_MODE=copy

# Install dependencies in a separate layer (cached)
# This layer only rebuilds when dependencies change
# Use --python-preference only-system to avoid symlink issues with UV-managed Python
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev --python-preference only-system

# Copy the entire project
COPY . /app

# Install the project itself (non-editable for production)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable --python-preference only-system

# -----------------------------------------------------------------------------
# Stage 2: Runtime - Minimal production image
# -----------------------------------------------------------------------------
FROM python:3.13-slim-bookworm

# Copy uv for running commands
COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /uvx /bin/

# Create non-root user for security with home directory
RUN groupadd -r appuser && useradd -r -g appuser -m -d /home/appuser appuser

# Set working directory
WORKDIR /app

# Copy only the virtual environment from builder (not source code since non-editable)
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

# Copy application code (needed for imports even with non-editable install)
COPY --chown=appuser:appuser ./app /app/app
COPY --chown=appuser:appuser ./pyproject.toml /app/pyproject.toml

# Activate virtual environment by adding to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Set Python to run in unbuffered mode (better for Docker logs)
ENV PYTHONUNBUFFERED=1

# Expose FastAPI port (8080 for AWS App Runner compatibility)
EXPOSE 8080

# Switch to non-root user
USER appuser

# Health check (optional - FastAPI usually has /health or /docs)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/docs').read()" || exit 1

# Run the application using the venv's python directly (bypasses uv's interpreter detection)
# Using port 8080 for AWS App Runner compatibility
CMD ["/app/.venv/bin/python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
