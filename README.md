# Whisper API - Speech-to-Text Service trên Railway

Project này cung cấp một REST API service để chuyển đổi giọng nói thành văn bản sử dụng OpenAI Whisper-small từ Hugging Face. API có thể được deploy lên Railway cloud platform.

## Cài đặt

### 1. Cài đặt các dependencies

```bash
pip install -r requirements.txt
```

### 2. Dependencies chính

- `torch`: PyTorch framework
- `transformers`: Hugging Face Transformers library
- `librosa`: Xử lý audio
- `numpy`: Xử lý array
- `accelerate`: Tăng tốc huấn luyện/inference
- `safetensors`: Load model an toàn
- `soundfile`: Đọc file audio

## Sử dụng

### Cách sử dụng cơ bản

```python
from whisper_connection import WhisperConnection

# Khởi tạo connection
whisper = WhisperConnection()

# Transcribe một file audio
result = whisper.transcribe("path/to/your/audio.wav")
print(f"Kết quả: {result}")

# Transcribe với ngôn ngữ cụ thể (tiếng Việt)
result = whisper.transcribe("audio.wav", language="vi")
print(f"Kết quả: {result}")
```

### Transcribe nhiều file cùng lúc

```python
# Transcribe batch
audio_files = ["file1.wav", "file2.wav", "file3.mp3"]
results = whisper.transcribe_batch(audio_files, language="vi")

for result in results:
    print(f"File: {result['file']}")
    print(f"Transcription: {result['transcription']}")
    print("-" * 50)
```

### Sử dụng với numpy array

```python
import librosa
import numpy as np

# Load audio với librosa
audio, sr = librosa.load("audio.wav", sr=16000)

# Transcribe từ numpy array
result = whisper.transcribe(audio, language="vi")
print(f"Kết quả: {result}")
```

## Các tính năng

### WhisperConnection Class

#### `__init__(model_name="openai/whisper-small")`

- Khởi tạo kết nối tới Whisper model
- Tự động detect GPU/CPU
- Load model và processor

#### `transcribe(audio, language=None)`

- Chuyển đổi audio thành text
- Hỗ trợ cả file path và numpy array
- Có thể chỉ định ngôn ngữ cụ thể

#### `transcribe_batch(audio_files, language=None)`

- Transcribe nhiều file audio cùng lúc
- Trả về list kết quả với file name và transcription

#### `load_audio(audio_path, target_sr=16000)`

- Load và preprocessing audio file
- Chuyển đổi sample rate về 16kHz (yêu cầu của Whisper)

## Các ngôn ngữ được hỗ trợ

Whisper hỗ trợ nhiều ngôn ngữ, một số mã ngôn ngữ phổ biến:

- `"vi"`: Tiếng Việt
- `"en"`: Tiếng Anh
- `"fr"`: Tiếng Pháp
- `"de"`: Tiếng Đức
- `"es"`: Tiếng Tây Ban Nha
- `"ja"`: Tiếng Nhật
- `"ko"`: Tiếng Hàn
- `"zh"`: Tiếng Trung

## Định dạng audio được hỗ trợ

- WAV
- MP3
- FLAC
- M4A
- OGG
- và nhiều định dạng khác (thông qua librosa)

## Yêu cầu hệ thống

- Python 3.8+
- RAM: Tối thiểu 4GB (8GB+ được khuyến nghị)
- GPU: Không bắt buộc nhưng sẽ tăng tốc đáng kể
- Dung lượng: ~1.5GB để tải model

## Chạy test

```bash
python whisper_connection.py
```

## Lưu ý

1. Lần chạy đầu tiên sẽ mất thời gian để tải model từ Hugging Face
2. Model sẽ được cache local cho các lần sử dụng sau
3. GPU sẽ tăng tốc quá trình inference đáng kể
4. Audio sẽ được tự động resample về 16kHz nếu cần thiết

## Troubleshooting

### Lỗi thiếu CUDA

Nếu gặp lỗi liên quan đến CUDA, cài đặt PyTorch với CUDA:

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Lỗi thiếu ffmpeg

Cài đặt ffmpeg để hỗ trợ nhiều định dạng audio hơn:

```bash
# Windows (với chocolatey)
choco install ffmpeg

# macOS (với homebrew)
brew install ffmpeg

# Ubuntu/Debian
sudo apt update
sudo apt install ffmpeg
```

### Out of Memory

Nếu gặp lỗi hết memory:

1. Giảm độ dài audio file
2. Sử dụng CPU thay vì GPU
3. Đóng các ứng dụng khác đang chạy

## 🚀 Deploy lên Railway

### 1. Chuẩn bị Repository

1. **Push code lên GitHub/GitLab**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Whisper API"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

### 2. Deploy trên Railway

1. **Đăng ký/Đăng nhập Railway**: Vào [railway.app](https://railway.app)

2. **Tạo New Project**:

   - Click "New Project"
   - Chọn "Deploy from GitHub repo"
   - Chọn repository của bạn

3. **Railway sẽ tự động**:
   - Detect Dockerfile
   - Build container
   - Deploy service
   - Cung cấp public URL

### 3. Cấu hình Environment Variables (Tùy chọn)

Trong Railway dashboard, bạn có thể set các environment variables:

- `PORT`: Port để chạy service (Railway tự set)
- `TRANSFORMERS_CACHE`: Thư mục cache model
- `HF_HOME`: Hugging Face cache directory

### 4. Sử dụng API sau khi deploy

Sau khi deploy thành công, bạn sẽ có URL dạng: `https://your-app-name.railway.app`

#### Endpoints chính:

- `GET /`: Thông tin cơ bản
- `GET /health`: Health check
- `GET /docs`: API documentation (Swagger UI)
- `POST /transcribe`: Transcribe file audio
- `POST /transcribe-batch`: Transcribe nhiều file
- `GET /languages`: Danh sách ngôn ngữ hỗ trợ

#### Ví dụ sử dụng API:

```bash
# Health check
curl https://your-app.railway.app/health

# Transcribe file audio
curl -X POST "https://your-app.railway.app/transcribe" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@audio.wav" \
  -F "language=vi"
```

#### Sử dụng với Python:

```python
import requests

# Transcribe audio
url = "https://your-app.railway.app/transcribe"
files = {"file": open("audio.wav", "rb")}
data = {"language": "vi"}

response = requests.post(url, files=files, data=data)
result = response.json()
print(result["transcription"])
```

#### Sử dụng với JavaScript:

```javascript
const formData = new FormData();
formData.append("file", audioFile);
formData.append("language", "vi");

fetch("https://your-app.railway.app/transcribe", {
  method: "POST",
  body: formData,
})
  .then((response) => response.json())
  .then((data) => console.log(data.transcription));
```

### 5. Monitoring và Logs

- **Railway Dashboard**: Xem logs, metrics, resource usage
- **Health Check**: `/health` endpoint để monitor service
- **Auto-scaling**: Railway tự động scale theo traffic

### 6. Custom Domain (Tùy chọn)

Trong Railway dashboard:

1. Vào Settings > Domains
2. Add custom domain
3. Configure DNS records

### 7. Pricing và Giới hạn

Railway free tier:

- $5 credit/tháng
- Unlimited projects
- Community support

Paid plans:

- Pay per usage
- More resources
- Priority support

### Lưu ý quan trọng:

1. **First deployment**: Lần đầu deploy sẽ mất 5-10 phút để tải model
2. **Memory usage**: Whisper model cần ~2GB RAM
3. **Cold starts**: Service có thể mất thời gian khởi động sau khi idle
4. **File size**: Giới hạn 25MB per file upload
5. **Timeout**: Request timeout ~30 seconds

## 🔧 Local Development

### Chạy API local:

```bash
# Cài dependencies
pip install -r requirements.txt

# Chạy server
python app.py

# Hoặc với uvicorn
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

API sẽ chạy tại: `http://localhost:8000`

- Docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

### Test với Docker:

```bash
# Build image
docker build -t whisper-api .

# Run container
docker run -p 8000:8000 whisper-api
```

## 📊 API Documentation

Sau khi chạy service, truy cập `/docs` để xem Swagger UI với:

- Chi tiết tất cả endpoints
- Try-it-out functionality
- Request/response schemas
- Error codes và meanings

## License

MIT License
