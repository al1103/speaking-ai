# Multi-stage build để giảm kích thước image
FROM python:3.11-slim as builder

# Cài đặt build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Tạo virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy và cài đặt Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

# Cài đặt chỉ runtime dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment từ builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Tạo non-root user để chạy app
RUN useradd --create-home --shell /bin/bash app
USER app
WORKDIR /home/app

# Copy source code với ownership cho user app
COPY --chown=app:app optimize_whisper.py .
COPY --chown=app:app app.py .

# Set environment variables
ENV TRANSFORMERS_CACHE=/tmp/model_cache
ENV HF_HOME=/tmp/model_cache
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5m --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Chạy ứng dụng
CMD ["python", "app.py"]
