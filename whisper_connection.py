#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kết nối tới OpenAI Whisper-small model từ Hugging Face
Sử dụng transformers library để thực hiện speech-to-text
"""

import torch
from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq
import librosa
import numpy as np
from typing import Union, Optional
import warnings

# Tắt các warning không cần thiết
warnings.filterwarnings("ignore")

class WhisperConnection:
    """
    Class để kết nối và sử dụng OpenAI Whisper-small model từ Hugging Face
    """

    def __init__(self, model_name: str = "openai/whisper-small"):
        """
        Khởi tạo kết nối tới Whisper model

        Args:
            model_name (str): Tên model trên Hugging Face (default: openai/whisper-small)
        """
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Đang sử dụng device: {self.device}")

        # Load processor và model
        print(f"Đang tải model {model_name}...")
        self.processor = AutoProcessor.from_pretrained(model_name)
        self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            low_cpu_mem_usage=True,
            use_safetensors=True
        )
        self.model.to(self.device)
        print("Model đã được tải thành công!")

    def load_audio(self, audio_path: str, target_sr: int = 16000) -> np.ndarray:
        """
        Load và preprocessing audio file

        Args:
            audio_path (str): Đường dẫn tới file audio
            target_sr (int): Sample rate mục tiêu (default: 16000)

        Returns:
            np.ndarray: Audio data đã được preprocessing
        """
        try:
            # Load audio với librosa
            audio, sr = librosa.load(audio_path, sr=target_sr)
            print(f"Đã load audio: {audio_path}")
            print(f"Duration: {len(audio) / sr:.2f} seconds")
            return audio
        except Exception as e:
            print(f"Lỗi khi load audio: {e}")
            return None

    def transcribe(self, audio: Union[str, np.ndarray], language: Optional[str] = None) -> str:
        """
        Chuyển đổi audio thành text

        Args:
            audio (Union[str, np.ndarray]): Đường dẫn tới file audio hoặc audio array
            language (Optional[str]): Ngôn ngữ (ví dụ: "vi" cho tiếng Việt, "en" cho tiếng Anh)

        Returns:
            str: Text đã được transcribe
        """
        try:
            # Nếu input là đường dẫn file, load audio
            if isinstance(audio, str):
                audio_data = self.load_audio(audio)
                if audio_data is None:
                    return "Lỗi: Không thể load audio file"
            else:
                audio_data = audio

            # Preprocessing audio
            inputs = self.processor(
                audio_data,
                sampling_rate=16000,
                return_tensors="pt"
            )

            # Chuyển input lên device
            input_features = inputs.input_features.to(self.device)

            # Thiết lập generation config
            generate_kwargs = {}
            if language:
                generate_kwargs["language"] = language

            # Generate transcription
            print("Đang thực hiện transcription...")
            with torch.no_grad():
                predicted_ids = self.model.generate(
                    input_features,
                    max_new_tokens=448,
                    **generate_kwargs
                )

            # Decode kết quả
            transcription = self.processor.batch_decode(
                predicted_ids,
                skip_special_tokens=True
            )[0]

            return transcription.strip()

        except Exception as e:
            print(f"Lỗi khi transcribe: {e}")
            return f"Lỗi: {e}"

    def transcribe_batch(self, audio_files: list, language: Optional[str] = None) -> list:
        """
        Transcribe nhiều file audio cùng lúc

        Args:
            audio_files (list): Danh sách đường dẫn tới các file audio
            language (Optional[str]): Ngôn ngữ

        Returns:
            list: Danh sách kết quả transcription
        """
        results = []
        for i, audio_file in enumerate(audio_files):
            print(f"Đang xử lý file {i+1}/{len(audio_files)}: {audio_file}")
            result = self.transcribe(audio_file, language)
            results.append({
                "file": audio_file,
                "transcription": result
            })
        return results

def main():
    """
    Hàm main để test kết nối và sử dụng model
    """
    print("=== Khởi tạo Whisper Connection ===")

    # Khởi tạo connection
    whisper = WhisperConnection()

    # Test với audio file (nếu có)
    # Uncomment và thay đổi đường dẫn file audio để test
    """
    audio_file = "path/to/your/audio.wav"
    if os.path.exists(audio_file):
        print(f"\n=== Test Transcription ===")
        result = whisper.transcribe(audio_file, language="vi")  # Sử dụng "vi" cho tiếng Việt
        print(f"Kết quả: {result}")
    else:
        print("Không tìm thấy file audio để test")
    """

    print("\n=== Model đã sẵn sàng sử dụng ===")
    print("Cách sử dụng:")
    print("1. whisper.transcribe('path/to/audio.wav') - Transcribe file audio")
    print("2. whisper.transcribe(audio_array) - Transcribe từ numpy array")
    print("3. whisper.transcribe_batch(['file1.wav', 'file2.wav']) - Transcribe nhiều file")

if __name__ == "__main__":
    main()
