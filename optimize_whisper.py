#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Optimized Whisper Connection cho Railway deployment
Giảm memory usage và tăng tốc độ loading
"""

import torch
from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq
import librosa
import numpy as np
from typing import Union, Optional
import warnings
import gc
import os

# Tắt các warning không cần thiết
warnings.filterwarnings("ignore")

class OptimizedWhisperConnection:
    """
    Optimized version của WhisperConnection cho deployment
    - Giảm memory usage
    - Faster loading
    - Better error handling
    """

    def __init__(self, model_name: str = "openai/whisper-small"):
        """
        Khởi tạo optimized Whisper model
        """
        self.model_name = model_name
        self.device = "cpu"  # Force CPU để tránh CUDA memory issues
        self.model = None
        self.processor = None

        print(f"Initializing optimized Whisper model: {model_name}")
        self._load_model()

    def _load_model(self):
        """Load model với optimizations"""
        try:
            print("Loading processor...")
            self.processor = AutoProcessor.from_pretrained(
                self.model_name,
                cache_dir=os.environ.get('TRANSFORMERS_CACHE', '/tmp/model_cache')
            )

            print("Loading model...")
            self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
                self.model_name,
                torch_dtype=torch.float32,  # Sử dụng float32 cho CPU
                low_cpu_mem_usage=True,
                use_safetensors=False,  # Giảm dependencies
                cache_dir=os.environ.get('TRANSFORMERS_CACHE', '/tmp/model_cache')
            )

            # Optimizations cho CPU inference
            self.model.eval()
            self.model = torch.jit.optimize_for_inference(self.model)

            print("Model loaded successfully!")

        except Exception as e:
            print(f"Error loading model: {e}")
            raise e

    def load_audio(self, audio_path: str, target_sr: int = 16000) -> np.ndarray:
        """Optimized audio loading"""
        try:
            audio, sr = librosa.load(audio_path, sr=target_sr, mono=True)

            # Normalize audio
            audio = librosa.util.normalize(audio)

            return audio
        except Exception as e:
            print(f"Error loading audio: {e}")
            return None

    def transcribe(self, audio: Union[str, np.ndarray], language: Optional[str] = None) -> str:
        """
        Optimized transcription
        """
        try:
            if self.model is None or self.processor is None:
                return "Error: Model not loaded"

            # Load audio if path provided
            if isinstance(audio, str):
                audio_data = self.load_audio(audio)
                if audio_data is None:
                    return "Error: Cannot load audio file"
            else:
                audio_data = audio

            # Preprocessing với optimization
            inputs = self.processor(
                audio_data,
                sampling_rate=16000,
                return_tensors="pt",
                padding=True
            )

            # Generation với optimization settings
            generate_kwargs = {
                "max_new_tokens": 448,
                "num_beams": 1,  # Giảm từ default để tăng tốc
                "do_sample": False,  # Deterministic output
                "use_cache": True
            }

            if language:
                generate_kwargs["language"] = language

            # Inference với torch.no_grad() để tiết kiệm memory
            with torch.no_grad():
                predicted_ids = self.model.generate(
                    inputs.input_features,
                    **generate_kwargs
                )

            # Decode result
            transcription = self.processor.batch_decode(
                predicted_ids,
                skip_special_tokens=True
            )[0]

            # Clean up memory
            del inputs, predicted_ids
            gc.collect()

            return transcription.strip()

        except Exception as e:
            print(f"Transcription error: {e}")
            return f"Error: {e}"

    def cleanup(self):
        """Cleanup resources để giải phóng memory"""
        if hasattr(self, 'model') and self.model is not None:
            del self.model
        if hasattr(self, 'processor') and self.processor is not None:
            del self.processor
        gc.collect()

# Singleton pattern để tránh load model nhiều lần
_whisper_instance = None

def get_whisper_instance():
    """Get singleton Whisper instance"""
    global _whisper_instance
    if _whisper_instance is None:
        _whisper_instance = OptimizedWhisperConnection()
    return _whisper_instance

def cleanup_whisper():
    """Cleanup Whisper instance"""
    global _whisper_instance
    if _whisper_instance is not None:
        _whisper_instance.cleanup()
        _whisper_instance = None
