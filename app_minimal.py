#!/usr/bin/env python3
"""
Minimal Whisper API for Railway deployment
Chỉ sử dụng essential dependencies
"""

from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import JSONResponse
import uvicorn
import os
import tempfile
import time
import requests

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
        "endpoints": ["/", "/health", "/test", "/transcribe", "/info"]
    }

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Transcribe audio file using HF Inference API
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")

        # Check file size (max 25MB)
        file_content = await file.read()
        if len(file_content) > 25 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large (max 25MB)")

        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file.write(file_content)
            temp_path = temp_file.name

        start_time = time.time()

        # Call HF API
        api_url = "https://api-inference.huggingface.co/models/openai/whisper-small"
        headers = {}

        # Add API key if available
        hf_key = os.environ.get('HF_API_KEY')
        if hf_key:
            headers["Authorization"] = f"Bearer {hf_key}"

        response = requests.post(
            api_url,
            headers=headers,
            data=file_content,
            timeout=60
        )

        processing_time = time.time() - start_time

        # Clean up temp file
        try:
            os.unlink(temp_path)
        except:
            pass

        if response.status_code == 200:
            result = response.json()
            transcription = result.get('text', 'No transcription available')

            return {
                "transcription": transcription,
                "filename": file.filename,
                "processing_time": round(processing_time, 2),
                "file_size": len(file_content),
                "api_provider": "Hugging Face",
                "timestamp": time.time()
            }
        elif response.status_code == 503:
            raise HTTPException(
                status_code=503,
                detail="Model đang loading, vui lòng thử lại sau 30-60 giây"
            )
        elif response.status_code == 429:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded, vui lòng thử lại sau"
            )
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"HF API Error: {response.text[:200]}"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal error: {str(e)}"
        )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))

    print(f"Starting minimal Whisper API on port {port}")

    uvicorn.run(
        "app_minimal:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )
