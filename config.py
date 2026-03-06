"""
Configuration file for TransLingo Pro
"""
import os

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24).hex()
    
    # Translation settings
    MAX_TEXT_LENGTH = 5000
    CACHE_EXPIRY_HOURS = 1
    MAX_HISTORY_ENTRIES = 50
    
    # Rate limiting
    RATE_LIMIT_REQUESTS = 50
    RATE_LIMIT_WINDOW = 3600  # 1 hour in seconds
    
    # TTS settings
    TTS_SUPPORTED_LANGUAGES = [
        "en", "fr", "ta", "es", "de", "it", "pt", "ja", 
        "ko", "zh", "ar", "hi", "ru"
    ]
    
    # Supported languages with names
    SUPPORTED_LANGUAGES = {
        "en": "English",
        "si": "Sinhala",
        "ta": "Tamil",
        "fr": "French",
        "es": "Spanish",
        "de": "German",
        "it": "Italian",
        "pt": "Portuguese",
        "ja": "Japanese",
        "ko": "Korean",
        "zh": "Chinese",
        "ar": "Arabic",
        "hi": "Hindi",
        "ru": "Russian",
        "nl": "Dutch",
        "pl": "Polish",
        "tr": "Turkish",
        "vi": "Vietnamese",
        "th": "Thai",
        "id": "Indonesian"
    }
    
    # Flask settings
    DEBUG = True
    TESTING = False
    
    # File paths
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    
    # Audio settings
    AUDIO_FORMAT = 'mp3'
    AUDIO_QUALITY = 'high'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    ENV = 'development'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    ENV = 'production'
    
    # Override with environment variables in production
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'prod-secret-key-change-this'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    ENV = 'testing'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
