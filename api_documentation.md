# WhisperX API Documentation

## Endpoint: `/v1/media/transcribe`

**Method:** `POST`  
**Content-Type:** `application/json`

The Media Transcription endpoint provides advanced audio/video transcription capabilities with speaker diarization, word-level timestamps, and multi-language support using WhisperX large-v3 model.

---

## 🚀 Quick Setup

### Prerequisites for Speaker Diarization

**1. Get Hugging Face Token (Free):**
- Visit: [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
- Create a **READ** token
- Copy the token

**2. Accept Model Terms:**
- Visit: [https://huggingface.co/pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)
- Click "Agree and access repository"

**3. Set Environment Variable:**
```yaml
# In docker-compose.yml
environment:
  - HUGGINGFACE_TOKEN=hf_your_actual_token_here
```

---

## Request Parameters

### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `media_url` | string | **Required.** Direct URL to the audio/video file. Must be accessible for download. |

### Optional Parameters

| Parameter | Type | Options | Default | Description |
|-----------|------|---------|---------|-------------|
| `task` | string | `transcribe`, `translate` | `transcribe` | Task type. `transcribe` converts speech to text, `translate` transcribes and translates to English. |
| `language` | string | See [Supported Languages](#supported-languages) | `null` (auto-detect) | Language code for the audio. If not specified, language will be automatically detected with 99%+ accuracy. |
| `output_format` | string | `json`, `srt`, `txt`, `vtt`, `all` | `json` | Output format for the transcription results. `all` returns all formats simultaneously. |
| `include_segments` | boolean | `true`, `false` | `true` | Include segmented transcription with timestamps in the response. |
| `include_word_timestamps` | boolean | `true`, `false` | `false` | Include word-level timestamps for precise timing of each word. Adds ~30% processing time. |
| `include_speaker_labels` | boolean | `true`, `false` | `false` | **⭐ NEW!** Enable speaker diarization to identify different speakers (SPEAKER_00, SPEAKER_01, etc.). Requires Hugging Face token. |
| `max_speakers` | integer | `1` to `20` | `null` (unlimited) | Maximum number of speakers to identify during diarization. Only used when `include_speaker_labels` is `true`. Recommended: 2-5 for meetings. |
| `beam_size` | integer | `1` to `10` | `5` | Beam size for transcription. Higher values = better accuracy but slower processing. Recommended: 5-8 for production. |
| `temperature` | float | `0.0` to `1.0` | `0.0` | Temperature for transcription sampling. `0.0` = deterministic, higher values = more creative/random. Keep at 0.0 for accuracy. |
| `max_words_per_line` | integer | `1` to `50` | `null` (no limit) | Maximum number of words per line in SRT format. Only applies when `output_format` is `srt` or `all`. Recommended: 6-10 for subtitles. |
| `id` | string | Any string | `null` | Custom identifier for tracking the transcription request. Useful for logging and debugging. |

---

## Supported Languages

The API supports automatic language detection or manual language specification using the following codes:

| Language | Code | Language | Code | Language | Code | Language | Code |
|----------|------|----------|------|----------|------|----------|------|
| English | `en` | French | `fr` | German | `de` | Spanish | `es` |
| Italian | `it` | Japanese | `ja` | Chinese | `zh` | Dutch | `nl` |
| Ukrainian | `uk` | Portuguese | `pt` | Arabic | `ar` | Russian | `ru` |
| Korean | `ko` | Polish | `pl` | Turkish | `tr` | Hindi | `hi` |
| Swedish | `sv` | Danish | `da` | Norwegian | `no` | Finnish | `fi` |

**Note:** Language auto-detection achieves 99%+ accuracy. Manual specification can improve performance for known languages.

---

## Response Format

### Success Response (HTTP 200)

```json
{
  "endpoint": "/v1/media/transcribe",
  "code": 200,
  "id": "meeting-transcription-001",
  "response": {
    "text": "Hello everyone, welcome to today's meeting. Thank you for joining us today.",
    "detected_language": "en",
    "segments": [
      {
        "start": 0.0,
        "end": 3.5,
        "text": "Hello everyone, welcome to today's meeting.",
        "speaker": "SPEAKER_00"
      },
      {
        "start": 4.0,
        "end": 6.8,
        "text": "Thank you for joining us today.",
        "speaker": "SPEAKER_01"
      }
    ],
    "word_segments": [
      {
        "word": "Hello",
        "start": 0.0,
        "end": 0.5,
        "score": 0.99,
        "speaker": "SPEAKER_00"
      },
      {
        "word": "everyone",
        "start": 0.6,
        "end": 1.2,
        "score": 0.98,
        "speaker": "SPEAKER_00"
      }
    ],
    "srt": "1\n00:00:00,000 --> 00:00:03,500\nHello everyone, welcome to today's meeting.\n\n2\n00:00:04,000 --> 00:00:06,800\nThank you for joining us today.\n\n",
    "txt": "Hello everyone, welcome to today's meeting. Thank you for joining us today.",
    "vtt": "WEBVTT\n\n00:00:00.000 --> 00:00:03.500\nHello everyone, welcome to today's meeting.\n\n00:00:04.000 --> 00:00:06.800\nThank you for joining us today.\n\n"
  },
  "message": "success",
  "processing_time": 42.3
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `endpoint` | string | The API endpoint that was called |
| `code` | integer | HTTP status code (200 = success) |
| `id` | string | The custom ID provided in the request (if any) |
| `response.text` | string | Complete transcription text with all speakers combined |
| `response.detected_language` | string | Auto-detected language code with confidence |
| `response.segments` | array | Segments with timestamps and speaker labels (if enabled) |
| `response.word_segments` | array | Word-level timestamps (if `include_word_timestamps` is true) |
| `response.srt` | string | SRT format subtitles (if `output_format` includes srt) |
| `response.txt` | string | Plain text format (if `output_format` includes txt) |
| `response.vtt` | string | WebVTT format (if `output_format` includes vtt) |
| `message` | string | Status message ("success" for successful transcriptions) |
| `processing_time` | float | Processing time in seconds |

---

## Error Response (HTTP 400/500)

```json
{
  "endpoint": "/v1/media/transcribe",
  "code": 400,
  "id": "your-custom-id",
  "response": null,
  "message": "Speaker diarization unavailable. Please set HUGGINGFACE_TOKEN environment variable and restart container.",
  "processing_time": 5.2
}
```

**Common Error Messages:**
- `"media_url is required"` - Missing required parameter
- `"Speaker diarization unavailable"` - Hugging Face token not set
- `"Failed to download file"` - URL inaccessible or invalid
- `"Invalid language code"` - Unsupported language specified

---

## Example Requests

### Basic Transcription
```bash
curl -X POST http://host.docker.internal:5772/v1/media/transcribe \
  -H "Content-Type: application/json" \
  -d '{
    "media_url": "http://host.docker.internal:9000/meeting-recordings/audio.wav",
    "id": "basic-transcription"
  }'
```

### 🎯 Speaker Diarization (Recommended for Meetings)
```bash
curl -X POST http://host.docker.internal:5772/v1/media/transcribe \
  -H "Content-Type: application/json" \
  -d '{
    "media_url": "http://host.docker.internal:9000/meeting-recordings/meeting.wav",
    "include_speaker_labels": true,
    "max_speakers": 5,
    "output_format": "all",
    "id": "meeting-with-speakers"
  }'
```

### Word-Level Timestamps for Precise Alignment
```bash
curl -X POST http://host.docker.internal:5772/v1/media/transcribe \
  -H "Content-Type: application/json" \
  -d '{
    "media_url": "http://host.docker.internal:9000/meeting-recordings/presentation.wav",
    "include_word_timestamps": true,
    "include_segments": true,
    "beam_size": 8,
    "id": "precise-timing"
  }'
```

### SRT Subtitle Generation
```bash
curl -X POST http://host.docker.internal:5772/v1/media/transcribe \
  -H "Content-Type: application/json" \
  -d '{
    "media_url": "http://host.docker.internal:9000/meeting-recordings/video.mp4",
    "output_format": "srt",
    "max_words_per_line": 8,
    "language": "en",
    "id": "subtitle-generation"
  }'
```

### Translation to English
```bash
curl -X POST http://host.docker.internal:5772/v1/media/transcribe \
  -H "Content-Type: application/json" \
  -d '{
    "media_url": "http://host.docker.internal:9000/meeting-recordings/spanish_audio.wav",
    "task": "translate",
    "language": "es",
    "id": "spanish-to-english"
  }'
```

### Ultimate Feature Test (All Features Combined)
```bash
curl -X POST http://host.docker.internal:5772/v1/media/transcribe \
  -H "Content-Type: application/json" \
  -d '{
    "media_url": "http://host.docker.internal:9000/meeting-recordings/conference.wav",
    "include_speaker_labels": true,
    "include_word_timestamps": true,
    "max_speakers": 8,
    "output_format": "all",
    "beam_size": 8,
    "max_words_per_line": 6,
    "id": "ultimate-transcription"
  }'
```

---

## Processing Times

**Performance benchmarks on NVIDIA RTX 3080 (12GB VRAM):**

| Audio Length | Basic Transcription | + Speaker Diarization | + Word Timestamps | All Features |
|--------------|--------------------|--------------------|------------------|--------------|
| 5 minutes | ~12 seconds | ~25 seconds | ~35 seconds | ~45 seconds |
| 15 minutes | ~25 seconds | ~45 seconds | ~60 seconds | ~80 seconds |
| 25 minutes | ~37 seconds | ~80 seconds | ~110 seconds | ~140 seconds |
| 60 minutes | ~90 seconds | ~180 seconds | ~240 seconds | ~300 seconds |

**Notes:**
- First request adds 30-60 seconds for model loading
- Speaker diarization adds ~2x processing time but provides valuable speaker identification
- Word timestamps add ~30% processing time
- Performance scales linearly with audio length

---

## Best Practices

### 🎯 Production Recommendations

1. **Speaker Diarization Setup:**
   - Always set `max_speakers` to expected number + 1-2 for better accuracy
   - Use 2-5 speakers for most meetings
   - Ensure Hugging Face token is properly configured

2. **Performance Optimization:**
   - Use `beam_size: 5-8` for production (balance speed/accuracy)
   - Enable only needed features to minimize processing time
   - Cache frequently used models with volume mounts

3. **File Handling:**
   - Ensure audio URLs are directly accessible without authentication
   - Support common formats: MP3, WAV, MP4, M4A, FLAC, OGG
   - No hard file size limits, but larger files take proportionally longer

4. **Error Handling:**
   - Implement timeout handling for long audio files
   - Check response codes and handle errors gracefully
   - Use custom `id` parameter for request tracking

5. **Container Networking:**
   - Use `host.docker.internal` for container-to-container communication
   - Configure proper network policies for production deployments
   - Monitor GPU memory usage for concurrent requests

### 🔒 Security Considerations

- **Tokens:** Keep Hugging Face tokens secure in environment variables
- **Network:** Restrict API access to trusted sources
- **Files:** Validate audio file URLs to prevent server-side request forgery
- **Resources:** Monitor GPU usage to prevent resource exhaustion

---

## Health Check Endpoint

### `GET /health`

Returns API health status and system information.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-06-19T00:00:00.000000",
  "version": "1.0.0"
}
```

**Use for:**
- Container orchestration health checks
- Load balancer health monitoring  
- Service discovery registration
- Automated deployment verification

---

## Container Integration

### N8N Workflow Integration

**HTTP Request Node Configuration:**
- **URL:** `http://host.docker.internal:5772/v1/media/transcribe`
- **Method:** `POST`
- **Headers:** `Content-Type: application/json`
- **Body:** JSON with transcription parameters
- **Timeout:** 300000ms (5 minutes) minimum

### MinIO Storage Integration

**Direct file access pattern:**
```
http://host.docker.internal:9000/bucket-name/path/to/audio.wav
```

### Telegram Bot Integration

**Workflow:** Telegram → N8N → WhisperX API → Response
- Handle large files (>20MB) via local Telegram server
- Process voice messages automatically
- Return transcriptions with speaker identification

---

**🎯 Ready for production use with enterprise-grade accuracy and performance!**