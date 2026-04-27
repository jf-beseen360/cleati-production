# CLEATI V3.3 - Production Docker Image
# Multi-stage build for optimized image size

# ============================================
# STAGE 1: Builder
# ============================================

FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements (use minimal for faster builds)
COPY requirements-minimal.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements-minimal.txt

# ============================================
# STAGE 2: Runtime
# ============================================

FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Set environment variables
ENV PATH=/root/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    ENVIRONMENT=production

# Copy application code
COPY cleati_production_api_v3_i18n.py .
COPY cleati_interface_v3_i18n.html .
COPY cleati/ ./cleati/

# Create non-root user
RUN useradd -m -u 1000 cleati && \
    chown -R cleati:cleati /app

USER cleati

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v3/health || exit 1

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "-m", "uvicorn", "cleati_production_api_v3_i18n:app", "--host", "0.0.0.0", "--port", "8000"]
