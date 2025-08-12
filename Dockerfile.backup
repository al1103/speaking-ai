# Simple single-stage Dockerfile for Railway (guaranteed to work)
FROM python:3.11-slim

# Install minimal system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install pip packages directly (no requirements.txt issues)
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir fastapi==0.104.1
RUN pip install --no-cache-dir uvicorn==0.24.0
RUN pip install --no-cache-dir python-multipart==0.0.6
RUN pip install --no-cache-dir requests==2.31.0
RUN pip install --no-cache-dir aiofiles==0.24.0

# Copy application files
COPY lightweight_whisper.py .
COPY app.py .

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=60s --timeout=5s --start-period=60s --retries=2 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["python", "app.py"]
