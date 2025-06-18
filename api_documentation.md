# WhisperX API Documentation

## Endpoint: `/v1/media/transcribe`

**Method:** `POST`  
**Content-Type:** `application/json`

The Media Transcription endpoint provides advanced audio/video transcription capabilities with speaker diarization, word-level timestamps, and multi-language support using WhisperX large-v3 model.

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
| `language` | string | See [Supported Languages](#supported-languages) | `null` (auto-detect) | Language code for the audio. If not specified, language will be automatically detected. |
| `output_format` | string | `json`, `srt`, `txt`, `vtt`, `all` | `json` | Output format for the transcription results. `all` returns all formats. |
| `include_segments` | boolean | `true`, `false` | `true` | Include segmented transcription with timestamps in the response. |
| `include_word_timestamps` | boolean | `true`, `false` | `false` | Include word-level timestamps for precise timing of each word. |
| `include_speaker_labels` | boolean | `true`, `false` | `false` | Enable speaker diarization to identify different speakers (SPEAKER_00, SPEAKER_01, etc.). |
| `max_speakers` | integer | `1` to `20` | `null` (unlimited) | Maximum number of speakers to identify during diarization. Only used when `include_speaker_labels` is `true`. |
| `beam_size` | integer | `1` to `10` | `5` | Beam size for transcription. Higher values = better accuracy but slower processing. |
| `temperature` | float | `0.0` to `1.0` | `0.0` | Temperature for transcription sampling. `0.0` = deterministic, higher values = more creative/random. |
| `max_words_per_line` | integer | `1` to `50` | `null` (no limit) | Maximum number of words per line in SRT format. Only applies when `output_format` is `srt` or `all`. |
| `id` | string | Any string | `null` | Custom identifier for tracking the transcription request. |

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

**Note:** If language is not specified or not in the supported list, the API will automatically detect the language.

---

## Response Format

### Success Response (HTTP 200)

```json
{
  "endpoint": "/v1/media/transcribe",
  "code": 200,
  "id": "your-custom-id",
  "response": {
    "text": "Complete transcription text...",
    "detected_language": "en",
    "segments": [
      {
        "start": 0.0,
        "end": 3.5,
        "text": "Hello, this is a test.",
        "speaker": "SPEAKER_00"
      }
    ],
    "word_segments": [
      {
        "word": "Hello",
        "start": 0.0,
        "end": 0.5,
        "score": 0.99,
        "speaker": "SPEAKER_00"
      }
    ],
    "speakers": [
      {
        "start": 0.0,
        "end": 10.5,
        "speaker": "SPEAKER_00"
      }
    ],
    "srt": "1\n00:00:00,000 --> 00:00:03,500\nHello, this is a test.\n\n",
    "txt": "Complete transcription text...",
    "vtt": "WEBVTT\n\n00:00:00.000 --> 00:00:03.500\nHello, this is a test.\n\n"
  },
  "message": "success",
  "processing_time": 36.66
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `endpoint` | string | The API endpoint that was called |
| `code` | integer | HTTP status code (200 = success) |
| `id` | string | The custom ID provided in the request (if any) |
| `response.text` | string | Complete transcription text |
| `response.detected_language` | string | Auto-detected language code |
| `response.segments` | array | Segments with timestamps (if `include_segments` is true) |
| `response.word_segments` | array | Word-level timestamps (if `include_word_timestamps` is true) |
| `response.speakers` | array | Speaker diarization results (if `include_speaker_labels` is true) |
| `response.srt` | string | SRT format subtitles (if `output_format` includes srt) |
| `response.txt` | string | Plain text format (if `output_format` includes txt) |
| `response.vtt` | string | WebVTT format (if `output_format` includes vtt) |
| `message` | string | Status message |
| `processing_time` | float | Processing time in seconds |

---

## Error Response (HTTP 400/500)

```json
{
  "endpoint": "/v1/media/transcribe",
  "code": 400,
  "id": "your-custom-id",
  "response": null,
  "message": "Error description",
  "processing_time": 0.0
}
```

---

## Example Requests

### Basic Transcription
```bash
curl -X POST http://localhost:5772/v1/media/transcribe \
  -H "Content-Type: application/json" \
  -d '{
    "media_url": "https://example.com/audio.wav"
  }'
```

### Speaker Diarization with Word Timestamps
```bash
curl -X POST http://localhost:5772/v1/media/transcribe \
  -H "Content-Type: application/json" \
  -d '{
    "media_url": "https://example.com/meeting.wav",
    "include_speaker_labels": true,
    "include_word_timestamps": true,
    "max_speakers": 5,
    "output_format": "all",
    "id": "meeting-transcription"
  }'
```

### SRT Subtitle Generation
```bash
curl -X POST http://localhost:5772/v1/media/transcribe \
  -H "Content-Type: application/json" \
  -d '{
    "media_url": "https://example.com/video.mp4",
    "output_format": "srt",
    "max_words_per_line": 8,
    "language": "en"
  }'
```

### Translation to English
```bash
curl -X POST http://localhost:5772/v1/media/transcribe \
  -H "Content-Type: application/json" \
  -d '{
    "media_url": "https://example.com/spanish_audio.wav",
    "task": "translate",
    "language": "es"
  }'
```

---

## Processing Times

Approximate processing times on NVIDIA RTX 3080:

| Audio Length | Basic Transcription | + Speaker Diarization | + Word Timestamps |
|--------------|--------------------|--------------------|------------------|
| 5 minutes | ~15 seconds | ~25 seconds | ~35 seconds |
| 15 minutes | ~30 seconds | ~50 seconds | ~70 seconds |
| 30 minutes | ~60 seconds | ~90 seconds | ~120 seconds |
| 60 minutes | ~120 seconds | ~180 seconds | ~240 seconds |

**Note:** First request may take additional 30-60 seconds for model loading.

---

## Best Practices

1. **File URLs:** Ensure audio/video URLs are directly accessible and not behind authentication
2. **Supported Formats:** MP3, WAV, MP4, M4A, FLAC, OGG, and most common formats
3. **File Size:** No hard limits, but larger files take proportionally longer to process
4. **Concurrent Requests:** API processes requests sequentially for optimal GPU usage
5. **Timeout:** Default timeout is 20 minutes (1200 seconds) for very long audio files

---

## Health Check Endpoint

### `GET /health`

Returns API health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-06-19T00:00:00.000000",
  "version": "1.0.0"
}
```