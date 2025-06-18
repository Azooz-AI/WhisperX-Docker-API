import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class Config:
    """Configuration class for WhisperX API"""
    
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')
    PORT = int(os.environ.get('PORT', 5772))
    HOST = os.environ.get('HOST', '0.0.0.0')
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # Timeout configuration (in seconds)
    TIMEOUT_SECONDS = int(os.environ.get('TIMEOUT_SECONDS', 1200))  # 20 minutes default
    
    # WhisperX default settings
    DEFAULT_MODEL = os.environ.get('DEFAULT_MODEL', 'large-v3')
    DEFAULT_DEVICE = 'cuda' if os.environ.get('FORCE_CPU', 'False').lower() != 'true' else 'cpu'
    DEFAULT_COMPUTE_TYPE = os.environ.get('DEFAULT_COMPUTE_TYPE', 'float16')
    DEFAULT_BATCH_SIZE = int(os.environ.get('DEFAULT_BATCH_SIZE', 16))
    
    # API configuration
    API_VERSION = 'v1'
    MAX_FILE_SIZE = int(os.environ.get('MAX_FILE_SIZE', 500 * 1024 * 1024))  # 500MB default
    
    # Supported languages for WhisperX
    SUPPORTED_LANGUAGES = [
        'en', 'fr', 'de', 'es', 'it', 'ja', 'zh', 'nl', 'uk', 'pt', 
        'ar', 'ru', 'ko', 'pl', 'tr', 'hi', 'sv', 'da', 'no', 'fi'
    ]
    
    # Output formats
    SUPPORTED_OUTPUT_FORMATS = ['json', 'srt', 'txt', 'vtt', 'all']
    
    # Task types
    SUPPORTED_TASKS = ['transcribe', 'translate']