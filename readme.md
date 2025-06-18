# WhisperX API Server

A Docker-based API server for WhisperX with multi-language transcription, speaker diarization, and word-level timestamps.

## Features

- ✅ Multi-language automatic speech recognition
- ✅ Speaker diarization (identify different speakers)
- ✅ Word-level timestamps
- ✅ Multiple output formats (JSON, SRT, TXT, VTT)
- ✅ GPU acceleration (NVIDIA CUDA)
- ✅ NCAA Toolkit-style API responses
- ✅ Configurable parameters

## Quick Start

### 1. Build the Docker Image

```bash
docker build -t whisperx-api .
```

### 2. Run the Container

```bash
docker run --gpus all -p 5772:5772 whisperx-api
```

### 3. Test the API

```bash
curl -X POST http://localhost:5772/v1/media/transcribe \
  -H "Content-Type: application/json" \
  -d '{
    "media_url": "https://your-minio-server.com/audio.mp3",
    "task": "transcribe",
    "include_speaker_labels": true,
    "output_format": "json"
  }'
```

## API Endpoints

### POST /v1/media/transcribe

Transcribe audio/video files with advanced features.

#### Required Parameters
- `media_url` (string): Direct URL to audio/video file

#### Optional Parameters
- `task` (string): "transcribe" or "translate" (default: "transcribe")
- `language` (string): Language code (e.g., "en", "fr") or auto-detect if not specified
- `output_format` (string): "json", "srt", "txt", "vtt", or "all" (default: "json")
- `include_word_timestamps` (boolean): Include word-level timestamps (default: false)
- `include_speaker_labels` (boolean): Include speaker diarization (default: false)
- `include_segments` (boolean): Include segment data (default: true)
- `max_speakers` (number): Maximum number of speakers for diarization
- `beam_size` (number): Beam size for transcription (default: 5)
- `temperature` (number): Temperature for transcription (0.0-1.0, default: 0.0)
- `max_words_per_line` (number): Max words per line in SRT format
- `id` (string): Custom job identifier

### GET /health

Health check endpoint.

## Environment Variables

- `PORT`: API port (default: 5772)
- `TIMEOUT_SECONDS`: Request timeout (default: 1200 = 20 minutes)
- `DEFAULT_MODEL`: WhisperX model (default: "large-v3")
- `DEBUG`: Enable debug mode (default: false)
- `FORCE_CPU`: Force CPU usage instead of GPU (default: false)

## Example Response

```json
{
  "endpoint": "/v1/media/transcribe",
  "code": 200,
  "id": "my-job-123",
  "response": {
    "text": "Hello, this is a test transcription.",
    "detected_language": "en",
    "segments": [
      {
        "start": 0.0,
        "end": 3.5,
        "text": "Hello, this is a test transcription.",
        "speaker": "SPEAKER_00"
      }
    ]
  },
  "message": "success",
  "processing_time": 45.2
}
```

## System Requirements

- Docker with GPU support
- NVIDIA GPU with 8GB+ VRAM
- NVIDIA Container Toolkit

## Notes

- First request may take longer due to model loading
- Large audio files (1+ hours) may take several minutes to process
- GPU memory is automatically cleaned after each request