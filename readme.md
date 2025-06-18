# WhisperX API Server

A Docker-based API server for WhisperX with multi-language transcription, speaker diarization, and word-level timestamps. Built for production use with N8N, automation workflows, and high-performance transcription tasks.

## ✨ Features

- ✅ **Multi-language automatic speech recognition** (20+ languages)
- ✅ **Speaker diarization** (identify different speakers: SPEAKER_00, SPEAKER_01, etc.)
- ✅ **Word-level timestamps** (precise timing for each word)
- ✅ **Multiple output formats** (JSON, SRT, TXT, VTT)
- ✅ **GPU acceleration** (NVIDIA CUDA optimized)
- ✅ **Production-ready API** (NCAA Toolkit-style responses)
- ✅ **Container networking** (works with N8N, MinIO, and other Docker services)
- ✅ **High performance** (37 seconds for 25-minute audio on RTX 3080)

## 🚀 Quick Start

### Prerequisites

- Docker with GPU support
- NVIDIA GPU with 8GB+ VRAM
- NVIDIA Container Toolkit
- [Hugging Face account](https://huggingface.co/join) (free - required for speaker diarization)

### 1. Clone or Create Project

Create a folder with these files:
- `Dockerfile`
- `docker-compose.yml`
- `requirements.txt`
- `app.py`
- `config.py`

### 2. Set Up Speaker Diarization (Optional but Recommended)

**Get Hugging Face Token:**
1. Go to [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
2. Create a **READ** token (free)
3. Copy the token

**Accept Model Terms:**
1. Visit [https://huggingface.co/pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)
2. Click "Agree and access repository"

**Add Token to docker-compose.yml:**
```yaml
environment:
  - HUGGINGFACE_TOKEN=hf_your_actual_token_here
```

### 3. Build and Run

```bash
docker-compose up --build
```

**Build time:** ~8-12 minutes  
**GPU memory usage:** ~6-8GB  
**Ready when you see:** "WhisperX model loaded successfully"

### 4. Test the API

**Health Check:**
```bash
curl http://localhost:5772/health
```

**Basic Transcription:**
```bash
curl -X POST http://localhost:5772/v1/media/transcribe \
  -H "Content-Type: application/json" \
  -d '{
    "media_url": "https://your-server.com/audio.wav"
  }'
```

**Speaker Diarization:**
```bash
curl -X POST http://localhost:5772/v1/media/transcribe \
  -H "Content-Type: application/json" \
  -d '{
    "media_url": "https://your-server.com/meeting.wav",
    "include_speaker_labels": true,
    "max_speakers": 5
  }'
```

## 📊 Performance Benchmarks

**Tested on NVIDIA RTX 3080 (12GB VRAM):**

| Audio Length | Basic Transcription | + Speaker Diarization | + Word Timestamps |
|--------------|--------------------|--------------------|------------------|
| 5 minutes | ~12 seconds | ~25 seconds | ~35 seconds |
| 15 minutes | ~25 seconds | ~45 seconds | ~60 seconds |
| 25 minutes | ~37 seconds | ~80 seconds | ~110 seconds |
| 60 minutes | ~90 seconds | ~180 seconds | ~240 seconds |

*First request adds 30-60 seconds for model loading*

## 🔗 Container Networking

**For N8N and other Docker containers, use:**
```
http://host.docker.internal:5772/v1/media/transcribe
```

**For external applications:**
```
http://localhost:5772/v1/media/transcribe
```

## 📖 API Documentation

### POST `/v1/media/transcribe`

**Required Parameters:**
- `media_url` (string): Direct URL to audio/video file

**Optional Parameters:**
- `include_speaker_labels` (boolean): Enable speaker diarization
- `include_word_timestamps` (boolean): Word-level timing
- `output_format` (string): "json", "srt", "txt", "vtt", "all"
- `language` (string): Force language or auto-detect
- `task` (string): "transcribe" or "translate"
- `max_speakers` (integer): Limit number of speakers
- `beam_size` (integer): Accuracy vs speed (1-10)
- `temperature` (float): Randomness (0.0-1.0)

**Example Response:**
```json
{
  "endpoint": "/v1/media/transcribe",
  "code": 200,
  "response": {
    "text": "Hello everyone, welcome to today's meeting.",
    "detected_language": "en",
    "segments": [
      {
        "start": 0.0,
        "end": 3.5,
        "text": "Hello everyone, welcome to today's meeting.",
        "speaker": "SPEAKER_00"
      }
    ]
  },
  "processing_time": 37.2
}
```

## 🛠️ Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `5772` | API server port |
| `TIMEOUT_SECONDS` | `1200` | Request timeout (20 minutes) |
| `DEFAULT_MODEL` | `large-v3` | WhisperX model |
| `HUGGINGFACE_TOKEN` | - | Required for speaker diarization |
| `DEBUG` | `false` | Enable debug logging |

## 🗣️ Supported Languages

English, French, German, Spanish, Italian, Japanese, Chinese, Dutch, Ukrainian, Portuguese, Arabic, Russian, Korean, Polish, Turkish, Hindi, Swedish, Danish, Norwegian, Finnish

## 🔧 Production Deployment

**Recommended Docker Compose:**
```yaml
version: '3.8'
services:
  whisperx-api:
    build: .
    ports:
      - "5772:5772"
    environment:
      - HUGGINGFACE_TOKEN=your_token_here
      - TIMEOUT_SECONDS=1200
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    restart: unless-stopped
    volumes:
      - whisper_cache:/root/.cache
```

## 🐛 Troubleshooting

**Model Loading Issues:**
- Ensure GPU has 8GB+ VRAM
- Check NVIDIA Container Toolkit installation
- Verify CUDA compatibility

**Speaker Diarization Fails:**
- Add Hugging Face token to environment
- Accept terms at pyannote model page
- Restart container after adding token

**Slow Performance:**
- Use smaller models for speed vs accuracy tradeoff
- Reduce `beam_size` parameter
- Monitor GPU memory usage

**Network Issues:**
- Use `host.docker.internal` for container-to-container communication
- Ensure audio URLs are directly accessible
- Check firewall settings for port 5772

## 🔒 Security Considerations

- Keep Hugging Face tokens secure
- Use environment variables, not hardcoded tokens
- Consider adding API authentication for production
- Restrict network access to trusted sources

## 📈 Use Cases

- **Meeting Transcription:** Automatic meeting notes with speaker identification
- **Podcast Processing:** Generate searchable transcripts with timestamps
- **Video Subtitles:** Create SRT files for video content
- **Multi-language Content:** Auto-detect and transcribe international audio
- **Automation Workflows:** Integrate with N8N for automated transcription pipelines
- **Content Analysis:** Extract insights from audio/video content

## 🤝 Contributing

Built for the community! Issues and improvements welcome.

## 📄 License

This project builds upon:
- [WhisperX](https://github.com/m-bain/whisperX) - Enhanced Whisper with alignment
- [OpenAI Whisper](https://github.com/openai/whisper) - Original speech recognition
- [pyannote.audio](https://github.com/pyannote/pyannote-audio) - Speaker diarization

---

**🎯 Ready for production use with N8N workflows, MinIO storage, and enterprise automation!**