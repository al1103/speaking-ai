# Ultra-lightweight multi-stage build for Railway
# Stage 1: Builder with Debian (better package compatibility)
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc6-dev \
    libsndfile1-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r /tmp/requirements.txt

# Stage 2: Ultra-minimal runtime
FROM python:3.11-slim

# Install only essential runtime libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create minimal user
RUN useradd --create-home --shell /bin/bash app
USER app
WORKDIR /home/app

# Copy only essential application files
COPY --chown=app:app lightweight_whisper.py .
COPY --chown=app:app app.py .

# Minimal environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

# Lightweight health check
HEALTHCHECK --interval=60s --timeout=5s --start-period=60s --retries=2 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "app.py"]
