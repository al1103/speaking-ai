#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ultra-lightweight Whisper service using external API
Không cần PyTorch/Transformers - giảm drastically image size
"""

import requests
import json
import os
import tempfile
import soundfile as sf
import numpy as np
from typing import Union, Optional
import asyncio
import aiofiles

class LightweightWhisperService:
    """
    Lightweight Whisper service sử dụng external API thay vì local model
    Giảm Docker image size từ 8GB xuống < 500MB
    """

        def __init__(self):
        # Ưu tiên sử dụng Hugging Face Inference API (miễn phí)
        self.api_url = "https://api-inference.huggingface.co/models/openai/whisper-small"
        self.model = "openai/whisper-small"

        # HF API key là optional (có thể chạy không cần key)
        self.api_key = os.environ.get('HF_API_KEY') or os.environ.get('HUGGINGFACE_API_KEY')
        self.use_hf = True  # Luôn sử dụng HF API

        print(f"Initialized Hugging Face Whisper Inference API")
        if self.api_key:
            print("Using authenticated HF API (higher rate limits)")
        else:
            print("Using free HF API (có rate limits nhưng vẫn hoạt động)")

    def preprocess_audio(self, audio_path: str) -> str:
        """
        Lightweight audio preprocessing
        """
        try:
            # Đọc audio file
            data, samplerate = sf.read(audio_path)

            # Convert to mono if stereo
            if len(data.shape) > 1:
                data = np.mean(data, axis=1)

            # Resample to 16kHz if needed (basic resampling)
            if samplerate != 16000:
                # Simple decimation/interpolation
                ratio = 16000 / samplerate
                new_length = int(len(data) * ratio)
                data = np.interp(np.linspace(0, len(data), new_length),
                               np.arange(len(data)), data)

            # Save preprocessed audio
            temp_path = audio_path + "_processed.wav"
            sf.write(temp_path, data, 16000)
            return temp_path

        except Exception as e:
            print(f"Error preprocessing audio: {e}")
            return audio_path  # Return original if preprocessing fails

        async def transcribe_with_hf(self, audio_path: str, language: Optional[str] = None) -> str:
        """
        Transcribe using Hugging Face Inference API (FREE)
        """
        try:
            processed_path = self.preprocess_audio(audio_path)

            # Setup headers
            headers = {
                "Content-Type": "audio/wav"
            }
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            # Đọc audio data
            async with aiofiles.open(processed_path, 'rb') as f:
                audio_data = await f.read()

            # HF Inference API parameters
            params = {}
            if language:
                # HF API có thể nhận language parameter
                params["language"] = language

            # Call Hugging Face Inference API
            response = requests.post(
                self.api_url,
                headers=headers,
                data=audio_data,
                params=params,
                timeout=60  # HF API có thể mất thời gian load model lần đầu
            )

            if response.status_code == 200:
                result = response.json()
                # HF API trả về format: {"text": "transcription"}
                if isinstance(result, dict):
                    return result.get('text', 'No transcription available')
                elif isinstance(result, list) and len(result) > 0:
                    return result[0].get('text', 'No transcription available')
                else:
                    return str(result)
            elif response.status_code == 503:
                return "Model đang loading, vui lòng thử lại sau 30-60 giây"
            elif response.status_code == 429:
                return "Rate limit exceeded, vui lòng thử lại sau"
            else:
                error_msg = f"HF API Error: {response.status_code}"
                try:
                    error_detail = response.json()
                    if 'error' in error_detail:
                        error_msg += f" - {error_detail['error']}"
                except:
                    error_msg += f" - {response.text[:200]}"
                return error_msg

        except requests.RequestException as e:
            return f"Network error: {str(e)}"
        except Exception as e:
            return f"Transcription error: {str(e)}"
        finally:
            # Cleanup preprocessed file
            if 'processed_path' in locals() and processed_path != audio_path:
                try:
                    os.unlink(processed_path)
                except:
                    pass

    async def transcribe_with_openai(self, audio_path: str, language: Optional[str] = None) -> str:
        """
        Transcribe using OpenAI API (PAID but higher quality)
        """
        try:
            if not self.api_key:
                return "Error: OpenAI API key not provided"

            processed_path = self.preprocess_audio(audio_path)

            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }

            files = {
                "file": open(processed_path, "rb"),
                "model": (None, self.model),
            }

            if language:
                files["language"] = (None, language)

            response = requests.post(
                self.api_url,
                headers=headers,
                files=files,
                timeout=30
            )

            files["file"].close()

            if response.status_code == 200:
                result = response.json()
                return result.get('text', 'No transcription available')
            else:
                return f"OpenAI API Error: {response.status_code}"

        except Exception as e:
            return f"OpenAI transcription error: {str(e)}"
        finally:
            # Cleanup
            if 'processed_path' in locals() and processed_path != audio_path:
                try:
                    os.unlink(processed_path)
                except:
                    pass

        async def transcribe(self, audio: Union[str, bytes], language: Optional[str] = None) -> str:
        """
        Main transcription method - luôn sử dụng Hugging Face API
        """
        # Handle bytes input (from uploaded files)
        if isinstance(audio, bytes):
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_file.write(audio)
                audio_path = temp_file.name
        else:
            audio_path = audio

        try:
            # Luôn sử dụng Hugging Face Inference API
            return await self.transcribe_with_hf(audio_path, language)
        finally:
            # Cleanup temporary file if created
            if isinstance(audio, bytes):
                try:
                    os.unlink(audio_path)
                except:
                    pass

# Fallback local implementation (very basic)
class FallbackWhisperService:
    """
    Fallback service khi không có API key
    Chỉ trả về mock response hoặc basic audio info
    """

    def __init__(self):
        print("Using fallback Whisper service (no API key provided)")

    async def transcribe(self, audio: Union[str, bytes], language: Optional[str] = None) -> str:
        try:
            # Basic audio analysis
            if isinstance(audio, bytes):
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                    temp_file.write(audio)
                    audio_path = temp_file.name
            else:
                audio_path = audio

            # Get audio info
            try:
                data, samplerate = sf.read(audio_path)
                duration = len(data) / samplerate

                return f"[Fallback Service] Audio processed: {duration:.2f}s, {samplerate}Hz. " \
                       f"Transcription unavailable without API key. " \
                       f"Set OPENAI_API_KEY or HF_API_KEY environment variable."
            except:
                return "[Fallback Service] Audio file processed, but transcription unavailable without API key."

        except Exception as e:
            return f"Fallback service error: {str(e)}"

# Singleton pattern
_whisper_service = None

def get_whisper_service():
    """Get whisper service instance - luôn sử dụng HF API"""
    global _whisper_service
    if _whisper_service is None:
        # Luôn sử dụng Hugging Face API (có thể hoạt động không cần key)
        _whisper_service = LightweightWhisperService()
    return _whisper_service
