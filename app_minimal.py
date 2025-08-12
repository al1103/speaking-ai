#!/usr/bin/env python3
"""
Minimal Whisper API for Railway deployment
Chỉ sử dụng essential dependencies
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import os
import time

# Simple FastAPI app without file uploads (test với URL first)
app = FastAPI(
    title="Minimal Whisper API",
    description="Ultra-lightweight Whisper API using HF Inference",
    version="1.0.0"
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Minimal Whisper API",
        "status": "running",
        "api_provider": "Hugging Face Inference API",
        "model": "openai/whisper-small"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "message": "Service is running"
    }

@app.get("/test")
async def test_hf_api():
    """Test HF API connection"""
    try:
        import requests

        # Test HF API endpoint
        response = requests.get(
            "https://api-inference.huggingface.co/models/openai/whisper-small",
            timeout=10
        )

        return {
            "hf_api_status": response.status_code,
            "hf_api_available": response.status_code in [200, 503],
            "message": "HF API connection test completed"
        }
    except Exception as e:
        return {
            "hf_api_status": "error",
            "error": str(e),
            "message": "HF API connection failed"
        }

@app.get("/info")
async def get_info():
    """API information"""
    return {
        "api_provider": "Hugging Face Inference API",
        "model": "openai/whisper-small",
        "supported_languages": ["vi", "en", "fr", "de", "es", "ja", "ko", "zh"],
        "free_tier_limits": "~1000 requests/hour",
        "note": "File upload coming soon - testing API connectivity first"
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))

    print(f"Starting minimal Whisper API on port {port}")

    uvicorn.run(
        "app_minimal:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )
