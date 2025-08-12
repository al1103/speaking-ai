# Absolute minimal Dockerfile for Railway
FROM python:3.11-slim

WORKDIR /app

# Install only essential packages one by one
RUN pip install --no-cache-dir fastapi==0.104.1
RUN pip install --no-cache-dir uvicorn==0.24.0
RUN pip install --no-cache-dir requests==2.31.0

# Copy minimal app
COPY app_minimal.py .

EXPOSE 8000

CMD ["python", "app_minimal.py"]
