# Star Office UI - Production Dockerfile
# 
# Multi-stage build for optimized production images:
# - Stage 1: Build and install dependencies
# - Stage 2: Minimal runtime image with only necessary files
#
# Features:
# - Multi-stage build for smaller image size
# - Non-root user for security
# - Health checks
# - Optimized layer caching
# - Build arguments for flexibility
#
# Build:
#   docker build -t star-office-ui:latest .
#
# Run:
#   docker run -d --name star-office-ui -p 5000:5000 star-office-ui:latest

# ============ Stage 1: Build ===========================================
FROM python:3.11-slim as builder

# Build arguments for flexibility
ARG BUILD_TARGET=production
ARG PYTHON_VERSION=3.11

# Set working directory
WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies first (better layer caching)
COPY backend/requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -r requirements.txt

# ============ Stage 2: Runtime =========================================
FROM python:3.11-slim as runtime

# Labels for image metadata
LABEL maintainer="Star Office Team"
LABEL description="Star Office UI - Real-time Agent Monitoring"
LABEL version="2.0.0"
LABEL build_date="${BUILD_DATE}"

# Build arguments
ARG BUILD_TARGET=production
ARG APP_USER=appuser
ARG APP_UID=1000
ARG APP_GID=1000

# Set working directory
WORKDIR /app

# Create non-root user for security
RUN groupadd --gid ${APP_GID} ${APP_USER} && \
    useradd --uid ${APP_UID} --gid ${APP_GID} --shell /bin/bash --create-home ${APP_USER}

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* && \
    apt-get clean

# Copy pre-built wheels and install
COPY --from=builder /build/wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

# Copy application code
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY backend/main.py ./main.py
COPY backend/init_db.py ./init_db.py

# Set proper permissions
RUN chown -R ${APP_USER}:${APP_USER} /app

# Create data directory
RUN mkdir -p /data && chown ${APP_USER}:${APP_USER} /data

# Switch to non-root user
USER ${APP_USER}

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    BUILD_TARGET=${BUILD_TARGET}

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/api/health')" || exit 1

# Set entrypoint
WORKDIR /app
ENTRYPOINT ["python", "main.py"]
