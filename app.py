#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Whisper API Server cho Railway deployment
FastAPI application để cung cấp Speech-to-Text service qua REST API
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import tempfile
import logging
from typing import Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time

from lightweight_whisper import get_whisper_service

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Khởi tạo FastAPI app
app = FastAPI(
    title="Whisper Speech-to-Text API",
    description="API service để chuyển đổi giọng nói thành văn bản sử dụng OpenAI Whisper",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Trong production nên giới hạn origins cụ thể
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
whisper_model = None
executor = ThreadPoolExecutor(max_workers=2)

def initialize_whisper():
    """Khởi tạo lightweight Whisper service"""
    global whisper_model
    try:
        logger.info("Đang khởi tạo lightweight Whisper service...")
        whisper_model = get_whisper_service()
        logger.info("Whisper service đã được khởi tạo thành công!")
        return True
    except Exception as e:
        logger.error(f"Lỗi khởi tạo Whisper service: {e}")
        return False

@app.on_event("startup")
async def startup_event():
    """Khởi tạo model khi app startup"""
    logger.info("Starting Whisper API Server...")
    success = await asyncio.get_event_loop().run_in_executor(
        executor, initialize_whisper
    )
    if not success:
        logger.error("Không thể khởi tạo Whisper model!")

@app.get("/")
async def root():
    """Root endpoint với thông tin cơ bản"""
    return {
        "message": "Whisper Speech-to-Text API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint cho Railway"""
    global whisper_model

    if whisper_model is None:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "message": "Whisper model chưa được khởi tạo",
                "timestamp": time.time()
            }
        )

    return {
        "status": "healthy",
        "message": "Service đang hoạt động bình thường",
        "model_loaded": whisper_model is not None,
        "timestamp": time.time()
    }

@app.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(..., description="File audio để transcribe"),
    language: Optional[str] = Form(None, description="Mã ngôn ngữ (vi, en, fr, etc.)")
):
    """
    Transcribe file audio thành text

    - **file**: File audio (wav, mp3, flac, m4a, ogg, etc.)
    - **language**: Mã ngôn ngữ (tùy chọn, ví dụ: 'vi' cho tiếng Việt)
    """
    global whisper_model

    if whisper_model is None:
        raise HTTPException(
            status_code=503,
            detail="Whisper model chưa được khởi tạo"
        )

    # Kiểm tra định dạng file
    allowed_extensions = ['.wav', '.mp3', '.flac', '.m4a', '.ogg', '.webm', '.mp4']
    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Định dạng file không được hỗ trợ. Các định dạng được hỗ trợ: {', '.join(allowed_extensions)}"
        )

    # Kiểm tra kích thước file (giới hạn 25MB)
    max_size = 25 * 1024 * 1024  # 25MB
    file_content = await file.read()

    if len(file_content) > max_size:
        raise HTTPException(
            status_code=413,
            detail="File quá lớn. Kích thước tối đa là 25MB"
        )

    try:
        # Tạo file tạm thời
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name

                # Thực hiện transcription với async
        start_time = time.time()
        transcription = await whisper_model.transcribe(temp_file_path, language=language)
        processing_time = time.time() - start_time

        # Xóa file tạm thời
        os.unlink(temp_file_path)

        return {
            "transcription": transcription,
            "filename": file.filename,
            "language": language,
            "processing_time": round(processing_time, 2),
            "file_size": len(file_content),
            "timestamp": time.time()
        }

    except Exception as e:
        # Đảm bảo xóa file tạm thời nếu có lỗi
        if 'temp_file_path' in locals():
            try:
                os.unlink(temp_file_path)
            except:
                pass

        logger.error(f"Lỗi khi transcribe: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi xử lý audio: {str(e)}"
        )

@app.post("/transcribe-batch")
async def transcribe_batch(
    files: list[UploadFile] = File(..., description="Danh sách file audio"),
    language: Optional[str] = Form(None, description="Mã ngôn ngữ")
):
    """
    Transcribe nhiều file audio cùng lúc
    """
    global whisper_model

    if whisper_model is None:
        raise HTTPException(
            status_code=503,
            detail="Whisper model chưa được khởi tạo"
        )

    if len(files) > 5:
        raise HTTPException(
            status_code=400,
            detail="Tối đa 5 file trong một batch"
        )

    results = []
    temp_files = []

    try:
        # Chuẩn bị tất cả file tạm thời
        for file in files:
            file_content = await file.read()

            # Kiểm tra kích thước
            if len(file_content) > 25 * 1024 * 1024:
                raise HTTPException(
                    status_code=413,
                    detail=f"File {file.filename} quá lớn (>25MB)"
                )

            # Tạo file tạm thời
            file_extension = os.path.splitext(file.filename)[1].lower()
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension)
            temp_file.write(file_content)
            temp_file.close()

            temp_files.append({
                'path': temp_file.name,
                'filename': file.filename,
                'size': len(file_content)
            })

                # Thực hiện transcription batch với async
        start_time = time.time()

        batch_results = []
        for temp_file_info in temp_files:
            try:
                transcription = await whisper_model.transcribe(
                    temp_file_info['path'],
                    language=language
                )
                batch_results.append({
                    "filename": temp_file_info['filename'],
                    "transcription": transcription,
                    "file_size": temp_file_info['size'],
                    "success": True
                })
            except Exception as e:
                batch_results.append({
                    "filename": temp_file_info['filename'],
                    "error": str(e),
                    "success": False
                })

        results = batch_results

        processing_time = time.time() - start_time

        return {
            "results": results,
            "total_files": len(files),
            "processing_time": round(processing_time, 2),
            "language": language,
            "timestamp": time.time()
        }

    except Exception as e:
        logger.error(f"Lỗi batch transcription: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi xử lý batch: {str(e)}"
        )

    finally:
        # Xóa tất cả file tạm thời
        for temp_file_info in temp_files:
            try:
                os.unlink(temp_file_info['path'])
            except:
                pass

@app.get("/languages")
async def get_supported_languages():
    """Lấy danh sách ngôn ngữ được hỗ trợ bởi Hugging Face Whisper API"""
    languages = {
        "vi": "Tiếng Việt",
        "en": "English",
        "fr": "Français",
        "de": "Deutsch",
        "es": "Español",
        "it": "Italiano",
        "pt": "Português",
        "ru": "Русский",
        "ja": "日本語",
        "ko": "한국어",
        "zh": "中文",
        "ar": "العربية",
        "hi": "हिन्दी",
        "th": "ไทย",
        "tr": "Türkçe",
        "pl": "Polski",
        "nl": "Nederlands",
        "sv": "Svenska",
        "da": "Dansk",
        "no": "Norsk"
    }

    return {
        "api_provider": "Hugging Face Inference API",
        "model": "openai/whisper-small",
        "supported_languages": languages,
        "total": len(languages),
        "note": "Sử dụng Hugging Face miễn phí với rate limits",
        "rate_limits": "~1000 requests/hour cho free tier"
    }

if __name__ == "__main__":
    # Cấu hình cho Railway
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"

    logger.info(f"Starting server on {host}:{port}")

    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=False,  # Tắt reload trong production
        log_level="info"
    )
