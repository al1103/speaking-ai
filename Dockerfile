# Ultra-lightweight multi-stage build for Railway
# Stage 1: Minimal builder
FROM python:3.11-alpine as builder

# Install minimal build dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install minimal Python dependencies
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt

# Stage 2: Ultra-minimal runtime
FROM python:3.11-alpine

# Install only essential runtime libraries
RUN apk add --no-cache \
    ffmpeg \
    libsndfile \
    curl \
    && rm -rf /var/cache/apk/*

# Copy virtual environment
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create minimal user
RUN adduser -D -h /app app
USER app
WORKDIR /app

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
