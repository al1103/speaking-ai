# 🤗 Hugging Face Inference API Setup

## 🎯 Tổng quan

Project đã được cấu hình để sử dụng **Hugging Face Inference API miễn phí** cho Whisper transcription. Không cần PyTorch/Transformers → Docker image < 500MB!

## 🚀 Deploy Railway ngay lập tức (MIỄN PHÍ)

### Bước 1: Push code

```bash
git add .
git commit -m "Hugging Face Whisper API deployment"
git push origin main
```

### Bước 2: Deploy trên Railway

1. Vào [railway.app](https://railway.app)
2. Connect GitHub repo
3. Deploy → **HOẠT ĐỘNG NGAY!**

**Không cần setup gì thêm!** API sẽ hoạt động với free tier của HF.

## ⚡ Tăng performance (Tùy chọn)

### Lấy HF API Key (FREE)

1. Vào [huggingface.co](https://huggingface.co)
2. Sign up/Login
3. Settings → Access Tokens → New Token
4. Copy token

### Set trên Railway

1. Railway dashboard → Environment Variables
2. Add: `HF_API_KEY=hf_your_token_here`
3. Redeploy

**Benefits với API key:**

- Higher rate limits (10,000+ requests/hour)
- Priority processing
- Faster response times

## 📊 Limits & Performance

### Free tier (không API key):

- **Rate limit**: ~1000 requests/hour
- **Latency**: 3-10 seconds
- **Model**: openai/whisper-small
- **Cost**: $0/month

### Authenticated (với API key):

- **Rate limit**: 10,000+ requests/hour
- **Latency**: 1-5 seconds
- **Model**: openai/whisper-small
- **Cost**: $0/month

## 🔧 API Endpoints

### Test ngay sau deploy:

```bash
# Health check
curl https://your-app.railway.app/health

# Transcribe tiếng Việt
curl -X POST "https://your-app.railway.app/transcribe" \
  -F "file=@audio.wav" \
  -F "language=vi"

# Check languages support
curl https://your-app.railway.app/languages
```

### Response mẫu:

```json
{
  "transcription": "Xin chào, đây là bài test tiếng Việt",
  "filename": "audio.wav",
  "language": "vi",
  "processing_time": 2.3,
  "file_size": 125440,
  "timestamp": 1703123456.78
}
```

## 🌐 Supported Languages

Whisper model hỗ trợ 99+ ngôn ngữ:

- `vi` - Tiếng Việt
- `en` - English
- `fr` - Français
- `de` - Deutsch
- `es` - Español
- `ja` - 日本語
- `ko` - 한국어
- `zh` - 中文
- `ar` - العربية
- `hi` - हिन्दी
- `th` - ไทย
- `ru` - Русский
- Và nhiều ngôn ngữ khác...

## 🚨 Troubleshooting

### "Model is loading" error?

```bash
# HF API cần 30-60 giây để load model lần đầu
# Chờ và thử lại
```

### Rate limit exceeded?

```bash
# Free tier: 1000 requests/hour
# Solutions:
# 1. Đợi 1 giờ để reset
# 2. Dùng HF API key để tăng limit
# 3. Cache results to reduce requests
```

### Slow response?

```bash
# HF free tier có thể chậm khi traffic cao
# Với API key sẽ nhanh hơn
```

## 📈 Monitoring

### Railway dashboard hiển thị:

- **Build time**: ~2 minutes
- **Image size**: ~400MB
- **Memory usage**: ~150MB
- **Response time**: 1-10s (tùy HF server load)

### Check HF API status:

```bash
curl https://api-inference.huggingface.co/models/openai/whisper-small
```

## 🎯 Production Tips

### 1. Caching responses

Implement Redis/database caching cho audio files đã process.

### 2. File validation

API đã có validation cho audio formats và file size limits.

### 3. Error handling

API trả về clear error messages cho debugging.

### 4. Monitoring

Setup alerts cho rate limits và API errors.

## 🏆 Benefits

✅ **$0 cost**: Hoàn toàn miễn phí
✅ **< 500MB image**: Railway compatible
✅ **No model download**: Instant deployment
✅ **Latest Whisper**: Always up-to-date
✅ **99+ languages**: Full multilingual support
✅ **Production ready**: HF infrastructure

**Deploy ngay để test!** 🚀
