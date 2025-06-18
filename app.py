import os
import time
import tempfile
import requests
import traceback
import gc
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import whisperx
import torch

from config import Config

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Global variables to store loaded models (for efficiency)
whisper_model = None
align_model = None
diarize_model = None
align_metadata = None

def load_whisper_model():
    """Load WhisperX model once at startup"""
    global whisper_model
    if whisper_model is None:
        print(f"Loading WhisperX model: {Config.DEFAULT_MODEL}")
        whisper_model = whisperx.load_model(
            Config.DEFAULT_MODEL, 
            device=Config.DEFAULT_DEVICE,
            compute_type=Config.DEFAULT_COMPUTE_TYPE
        )
        print("WhisperX model loaded successfully")
    return whisper_model

def load_alignment_model(language_code):
    """Load alignment model for specific language"""
    global align_model, align_metadata
    try:
        model_key = f"{language_code}_{Config.DEFAULT_DEVICE}"
        if align_model is None or getattr(align_model, '_language', None) != language_code:
            print(f"Loading alignment model for language: {language_code}")
            align_model, align_metadata = whisperx.load_align_model(
                language_code=language_code, 
                device=Config.DEFAULT_DEVICE
            )
            align_model._language = language_code  # Store language for reference
            print(f"Alignment model loaded for {language_code}")
        return align_model, align_metadata
    except Exception as e:
        print(f"Warning: Could not load alignment model for {language_code}: {e}")
        return None, None

def load_diarization_model():
    """Load speaker diarization model using pyannote directly"""
    global diarize_model
    if diarize_model is None:
        print("Loading diarization model...")
        try:
            # Check for Hugging Face token in environment
            hf_token = os.environ.get('HUGGINGFACE_TOKEN') or os.environ.get('HF_TOKEN')
            if not hf_token:
                raise Exception("Speaker diarization requires a Hugging Face token. Please set HUGGINGFACE_TOKEN environment variable. Get your token at: https://huggingface.co/settings/tokens")
            
            # Try to use whisperx.DiarizationPipeline first
            try:
                diarize_model = whisperx.DiarizationPipeline(
                    use_auth_token=hf_token,
                    device=Config.DEFAULT_DEVICE
                )
                print("Diarization model loaded successfully via WhisperX")
            except AttributeError:
                print("WhisperX DiarizationPipeline not found, using pyannote directly...")
                # Use pyannote directly as fallback
                from pyannote.audio import Pipeline
                diarize_model = Pipeline.from_pretrained(
                    "pyannote/speaker-diarization-3.1",
                    use_auth_token=hf_token
                ).to(torch.device(Config.DEFAULT_DEVICE))
                print("Diarization model loaded successfully via pyannote")
                
        except Exception as e:
            print(f"Failed to load diarization model: {e}")
            return None
    return diarize_model

def download_file_from_url(url):
    """Download file from URL to temporary location"""
    try:
        print(f"Downloading file from: {url}")
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.audio')
        
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                temp_file.write(chunk)
        
        temp_file.close()
        print(f"File downloaded to: {temp_file.name}")
        return temp_file.name
    except Exception as e:
        raise Exception(f"Failed to download file: {str(e)}")

def format_transcription_output(result, segments, word_segments, speakers_result, params):
    """Format the transcription result according to requested output format"""
    
    # Base response structure
    response_data = {
        "text": result.get("text", ""),
        "detected_language": result.get("language", "unknown")
    }
    
    # Add segments if requested
    if params.get("include_segments", True):
        response_data["segments"] = segments
    
    # Add word-level timestamps if requested
    if params.get("include_word_timestamps", False) and word_segments:
        response_data["word_segments"] = word_segments
    
    # Add speaker labels if requested and available
    if params.get("include_speaker_labels", False) and speakers_result:
        response_data["speakers"] = speakers_result.get("segments", [])
    
    # Handle different output formats
    output_format = params.get("output_format", "json")
    
    if output_format == "srt" or output_format == "all":
        response_data["srt"] = generate_srt(segments, params.get("max_words_per_line"))
    
    if output_format == "txt" or output_format == "all":
        response_data["txt"] = result.get("text", "")
    
    if output_format == "vtt" or output_format == "all":
        response_data["vtt"] = generate_vtt(segments)
    
    return response_data

def generate_srt(segments, max_words_per_line=None):
    """Generate SRT format from segments"""
    srt_content = ""
    for i, segment in enumerate(segments, 1):
        start_time = format_timestamp(segment.get("start", 0))
        end_time = format_timestamp(segment.get("end", 0))
        text = segment.get("text", "").strip()
        
        # Handle max words per line
        if max_words_per_line and max_words_per_line > 0:
            words = text.split()
            lines = []
            for j in range(0, len(words), max_words_per_line):
                lines.append(" ".join(words[j:j + max_words_per_line]))
            text = "\n".join(lines)
        
        srt_content += f"{i}\n{start_time} --> {end_time}\n{text}\n\n"
    
    return srt_content

def generate_vtt(segments):
    """Generate VTT format from segments"""
    vtt_content = "WEBVTT\n\n"
    for segment in segments:
        start_time = format_timestamp(segment.get("start", 0), vtt_format=True)
        end_time = format_timestamp(segment.get("end", 0), vtt_format=True)
        text = segment.get("text", "").strip()
        vtt_content += f"{start_time} --> {end_time}\n{text}\n\n"
    
    return vtt_content

def format_timestamp(seconds, vtt_format=False):
    """Format timestamp for SRT/VTT"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millisecs = int((seconds % 1) * 1000)
    
    if vtt_format:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millisecs:03d}"
    else:
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })

@app.route(f'/{Config.API_VERSION}/media/transcribe', methods=['POST'])
def transcribe_media():
    """Main transcription endpoint following NCAA toolkit style"""
    start_time = time.time()
    temp_file_path = None
    
    try:
        # Validate request
        if not request.is_json:
            return jsonify({
                "endpoint": f"/{Config.API_VERSION}/media/transcribe",
                "code": 400,
                "message": "Content-Type must be application/json"
            }), 400
        
        data = request.get_json()
        
        # Validate required parameters
        if not data.get('media_url'):
            return jsonify({
                "endpoint": f"/{Config.API_VERSION}/media/transcribe",
                "code": 400,
                "message": "media_url is required"
            }), 400
        
        # Extract parameters with defaults and type conversion
        params = {
            "media_url": data.get("media_url"),
            "task": data.get("task", "transcribe"),
            "language": data.get("language"),  # None = auto-detect
            "output_format": data.get("output_format", "json"),
            "include_word_timestamps": str(data.get("include_word_timestamps", False)).lower() == "true",
            "include_speaker_labels": str(data.get("include_speaker_labels", False)).lower() == "true",
            "include_segments": str(data.get("include_segments", True)).lower() == "true",
            "max_speakers": int(data.get("max_speakers", 0)) if data.get("max_speakers") else None,
            "beam_size": int(data.get("beam_size", 5)),
            "temperature": float(data.get("temperature", 0.0)),
            "max_words_per_line": int(data.get("max_words_per_line", 0)) if data.get("max_words_per_line") else None,
            "id": data.get("id")
        }
        
        # Validate parameters
        if params["task"] not in Config.SUPPORTED_TASKS:
            return jsonify({
                "endpoint": f"/{Config.API_VERSION}/media/transcribe",
                "code": 400,
                "message": f"Invalid task. Supported: {Config.SUPPORTED_TASKS}"
            }), 400
        
        if params["output_format"] not in Config.SUPPORTED_OUTPUT_FORMATS:
            return jsonify({
                "endpoint": f"/{Config.API_VERSION}/media/transcribe",
                "code": 400,
                "message": f"Invalid output_format. Supported: {Config.SUPPORTED_OUTPUT_FORMATS}"
            }), 400
        
        # Download audio file
        temp_file_path = download_file_from_url(params["media_url"])
        
        # Load WhisperX model
        model = load_whisper_model()
        
        # Transcribe audio
        print("Starting transcription...")
        result = model.transcribe(
            temp_file_path,
            batch_size=Config.DEFAULT_BATCH_SIZE,
            language=params["language"],
            task=params["task"]
        )
        
        segments = result["segments"]
        detected_language = result["language"]
        word_segments = None
        speakers_result = None
        
        # Word-level alignment if requested
        if params["include_word_timestamps"]:
            print("Performing word-level alignment...")
            align_model_obj, metadata = load_alignment_model(detected_language)
            if align_model_obj and metadata:
                result_aligned = whisperx.align(
                    segments, 
                    align_model_obj, 
                    metadata, 
                    temp_file_path, 
                    Config.DEFAULT_DEVICE,
                    return_char_alignments=False
                )
                segments = result_aligned["segments"]
                word_segments = result_aligned.get("word_segments")
        
        # Speaker diarization if requested
        if params["include_speaker_labels"]:
            print("Performing speaker diarization...")
            diarize_model_obj = load_diarization_model()
            if diarize_model_obj is None:
                return jsonify({
                    "endpoint": f"/{Config.API_VERSION}/media/transcribe",
                    "code": 400,
                    "id": params.get("id"),
                    "response": None,
                    "message": "Speaker diarization unavailable. Please set HUGGINGFACE_TOKEN environment variable and restart container. Get token at: https://huggingface.co/settings/tokens",
                    "processing_time": round(time.time() - start_time, 2)
                }), 400
            
            try:
                print(f"Diarization model type: {type(diarize_model_obj)}")
                print(f"Processing audio file: {temp_file_path}")
                
                # Check if using WhisperX DiarizationPipeline or pyannote directly
                if hasattr(diarize_model_obj, '__class__') and 'Pipeline' in str(type(diarize_model_obj)):
                    print("Using pyannote Pipeline directly")
                    # Use the audio file path directly as pyannote can handle it better
                    diarize_segments = diarize_model_obj(temp_file_path)
                    print(f"Diarization completed, segments type: {type(diarize_segments)}")
                else:
                    print("Using WhisperX DiarizationPipeline")
                    diarize_segments = diarize_model_obj(temp_file_path)
                
                print("Assigning speakers to words...")
                
                # Convert pyannote format to WhisperX format if needed
                if hasattr(diarize_segments, 'itertracks'):
                    # Convert pyannote Annotation to WhisperX format
                    print("Converting pyannote format to WhisperX format...")
                    whisperx_segments = []
                    for turn, _, speaker in diarize_segments.itertracks(yield_label=True):
                        whisperx_segments.append({
                            'start': turn.start,
                            'end': turn.end,
                            'speaker': speaker
                        })
                    
                    # Create a simple object that whisperx.assign_word_speakers can use
                    class DiarizeResult:
                        def __init__(self, segments):
                            self.segments = segments
                    
                    diarize_result = DiarizeResult(whisperx_segments)
                    print(f"Converted {len(whisperx_segments)} speaker segments")
                    
                    # Manual speaker assignment instead of using whisperx.assign_word_speakers
                    print("Performing manual speaker assignment...")
                    transcription_segments = result_aligned['segments'] if 'result_aligned' in locals() else result['segments']
                    
                    for segment in transcription_segments:
                        segment_start = segment['start']
                        segment_end = segment['end']
                        
                        # Find the speaker with the most overlap
                        best_speaker = None
                        max_overlap = 0
                        
                        for speaker_seg in whisperx_segments:
                            overlap_start = max(segment_start, speaker_seg['start'])
                            overlap_end = min(segment_end, speaker_seg['end'])
                            overlap = max(0, overlap_end - overlap_start)
                            
                            if overlap > max_overlap:
                                max_overlap = overlap
                                best_speaker = speaker_seg['speaker']
                        
                        if best_speaker:
                            segment['speaker'] = best_speaker
                        else:
                            segment['speaker'] = 'SPEAKER_00'  # Default
                    
                    segments = transcription_segments
                    print(f"Manual speaker assignment completed. Found speakers: {set(seg.get('speaker', 'UNKNOWN') for seg in segments)}")
                    
                else:
                    # Use WhisperX format directly
                    print("Using WhisperX format directly...")
                    speakers_result = whisperx.assign_word_speakers(diarize_segments, result_aligned if 'result_aligned' in locals() else result)
                    if 'segments' in speakers_result:
                        segments = speakers_result["segments"]
                        print(f"WhisperX speaker assignment completed. Found {len(segments)} segments")
                    
            except Exception as diarization_error:
                error_message = str(diarization_error)
                print(f"Full diarization error: {error_message}")
                print(f"Error type: {type(diarization_error)}")
                import traceback
                print(f"Full traceback: {traceback.format_exc()}")
                return jsonify({
                    "endpoint": f"/{Config.API_VERSION}/media/transcribe",
                    "code": 400,
                    "id": params.get("id"),
                    "response": None,
                    "message": f"Speaker diarization failed: {error_message}. You may need to accept terms at: https://huggingface.co/pyannote/speaker-diarization-3.1",
                    "processing_time": round(time.time() - start_time, 2)
                }), 400
        
        # Format output
        response_data = format_transcription_output(result, segments, word_segments, speakers_result, params)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Clean up GPU memory
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()
        
        return jsonify({
            "endpoint": f"/{Config.API_VERSION}/media/transcribe",
            "code": 200,
            "id": params.get("id"),
            "response": response_data,
            "message": "success",
            "processing_time": round(processing_time, 2)
        })
        
    except Exception as e:
        error_msg = str(e)
        print(f"Error in transcription: {error_msg}")
        print(traceback.format_exc())
        
        return jsonify({
            "endpoint": f"/{Config.API_VERSION}/media/transcribe",
            "code": 500,
            "id": data.get("id") if 'data' in locals() else None,
            "response": None,
            "message": f"Internal server error: {error_msg}",
            "processing_time": round(time.time() - start_time, 2) if 'start_time' in locals() else 0
        }), 500
    
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except:
                pass

if __name__ == '__main__':
    print("Starting WhisperX API Server...")
    print(f"Device: {Config.DEFAULT_DEVICE}")
    print(f"Model: {Config.DEFAULT_MODEL}")
    print(f"Port: {Config.PORT}")
    print(f"Timeout: {Config.TIMEOUT_SECONDS} seconds")
    
    # Pre-load the main model to avoid delays on first request
    load_whisper_model()
    
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG,
        threaded=True
    )