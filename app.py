from flask import Flask, render_template, request, jsonify, session, send_file
from deep_translator import GoogleTranslator
from langdetect import detect, detect_langs
from gtts import gTTS
import os
import uuid
import hashlib
import json
import csv
import re
from datetime import datetime, timedelta
from functools import wraps
import string
from collections import Counter
import time
import socket
import urllib.request
from urllib.error import URLError

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# ==================== DATA STRUCTURES ====================
# Store translation history and cache
history = []
translation_cache = {}  # Cache for faster repeated translations
language_stats = {}  # Track language usage statistics
session_data = {}  # Store per-session data

# ==================== LANGUAGE CONFIGURATION ====================
# Supported TTS languages
tts_supported = ["en", "fr", "ta", "es", "de", "it", "pt", "ja", "ko", "zh", "ar", "hi", "ru"]

# Language names mapping
LANGUAGE_NAMES = {
    "en": "English", "si": "Sinhala", "ta": "Tamil", "fr": "French",
    "es": "Spanish", "de": "German", "it": "Italian", "pt": "Portuguese",
    "ja": "Japanese", "ko": "Korean", "zh": "Chinese", "ar": "Arabic",
    "hi": "Hindi", "ru": "Russian", "nl": "Dutch", "pl": "Polish",
    "tr": "Turkish", "vi": "Vietnamese", "th": "Thai", "id": "Indonesian"
}

# ==================== UTILITY CLASSES ====================
class TextAnalyzer:
    """Advanced text analysis utility class"""
    
    @staticmethod
    def calculate_readability(text):
        """Calculate Flesch Reading Ease score"""
        sentences = len(re.findall(r'[.!?]+', text))
        words = len(text.split())
        syllables = TextAnalyzer.count_syllables(text)
        
        if sentences == 0 or words == 0:
            return 0
        
        score = 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)
        return max(0, min(100, score))
    
    @staticmethod
    def count_syllables(text):
        """Estimate syllable count"""
        words = text.lower().split()
        syllable_count = 0
        for word in words:
            word = re.sub(r'[^a-z]', '', word)
            if len(word) <= 3:
                syllable_count += 1
            else:
                syllable_count += len(re.findall(r'[aeiouy]+', word))
        return max(1, syllable_count)
    
    @staticmethod
    def detect_text_type(text):
        """Detect if text is formal, casual, technical, etc."""
        formal_indicators = len(re.findall(r'\b(therefore|however|furthermore|consequently|moreover)\b', text.lower()))
        casual_indicators = len(re.findall(r'\b(yeah|nah|cool|awesome|gonna|wanna)\b', text.lower()))
        technical_indicators = len(re.findall(r'\b(algorithm|function|parameter|method|implementation)\b', text.lower()))
        
        scores = {
            'formal': formal_indicators,
            'casual': casual_indicators,
            'technical': technical_indicators
        }
        
        return max(scores, key=scores.get) if any(scores.values()) else 'neutral'
    
    @staticmethod
    def get_text_complexity(text):
        """Analyze text complexity"""
        words = text.split()
        if not words:
            return "N/A"
        
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        if avg_word_length < 4:
            return "Simple"
        elif avg_word_length < 6:
            return "Moderate"
        else:
            return "Complex"

class TranslationCache:
    """Caching system for translations"""
    
    @staticmethod
    def generate_key(text, source, target):
        """Generate cache key from text and languages"""
        content = f"{text}_{source}_{target}"
        return hashlib.md5(content.encode()).hexdigest()
    
    @staticmethod
    def get(text, source, target):
        """Retrieve cached translation"""
        key = TranslationCache.generate_key(text, source, target)
        if key in translation_cache:
            cached = translation_cache[key]
            # Check if cache is less than 1 hour old
            if datetime.now() - cached['timestamp'] < timedelta(hours=1):
                return cached['translation']
        return None
    
    @staticmethod
    def set(text, source, target, translation):
        """Store translation in cache"""
        key = TranslationCache.generate_key(text, source, target)
        translation_cache[key] = {
            'translation': translation,
            'timestamp': datetime.now()
        }

class LanguageDetector:
    """Enhanced language detection with confidence"""
    
    @staticmethod
    def detect_with_confidence(text):
        """Detect language with confidence score"""
        try:
            detections = detect_langs(text)
            if detections:
                primary = detections[0]
                return {
                    'language': primary.lang,
                    'confidence': round(primary.prob * 100, 2),
                    'alternatives': [{'lang': d.lang, 'prob': round(d.prob * 100, 2)} for d in detections[1:3]]
                }
        except:
            pass
        return {'language': 'en', 'confidence': 50, 'alternatives': []}

class TextPreprocessor:
    """Text preprocessing and cleaning"""
    
    @staticmethod
    def clean_text(text):
        """Clean and normalize text"""
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Remove control characters
        text = ''.join(char for char in text if char.isprintable())
        return text
    
    @staticmethod
    def validate_input(text, max_length=5000):
        """Validate input text"""
        if not text or not text.strip():
            return False, "Text cannot be empty"
        if len(text) > max_length:
            return False, f"Text exceeds maximum length of {max_length} characters"
        return True, ""
    
    @staticmethod
    def get_word_frequency(text, top_n=10):
        """Get most common words"""
        words = re.findall(r'\w+', text.lower())
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'is', 'are'}
        words = [w for w in words if w not in stop_words and len(w) > 2]
        return Counter(words).most_common(top_n)

class StatisticsManager:
    """Manage and track translation statistics"""
    
    @staticmethod
    def update_language_stats(source, target):
        """Update language pair statistics"""
        pair = f"{source}_to_{target}"
        language_stats[pair] = language_stats.get(pair, 0) + 1
    
    @staticmethod
    def get_most_used_pairs(top_n=5):
        """Get most frequently used language pairs"""
        return sorted(language_stats.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    @staticmethod
    def get_total_translations():
        """Get total number of translations"""
        return sum(language_stats.values())
    
    @staticmethod
    def get_session_stats(session_id):
        """Get statistics for current session"""
        if session_id not in session_data:
            return {'translations': 0, 'chars_translated': 0, 'words_translated': 0}
        return session_data[session_id]

# ==================== RATE LIMITING ====================
class RateLimiter:
    """Simple rate limiting"""
    request_history = {}
    
    @staticmethod
    def is_allowed(identifier, max_requests=50, window_seconds=3600):
        """Check if request is allowed"""
        now = time.time()
        if identifier not in RateLimiter.request_history:
            RateLimiter.request_history[identifier] = []
        
        # Clean old requests
        RateLimiter.request_history[identifier] = [
            t for t in RateLimiter.request_history[identifier] 
            if now - t < window_seconds
        ]
        
        # Check limit
        if len(RateLimiter.request_history[identifier]) >= max_requests:
            return False
        
        RateLimiter.request_history[identifier].append(now)
        return True

# ==================== CONNECTIVITY CHECKER ====================
class ConnectivityChecker:
    """Check internet and service connectivity"""
    
    @staticmethod
    def check_internet(timeout=3):
        """Check if internet connection is available"""
        try:
            # Try to connect to Google's DNS
            socket.create_connection(("8.8.8.8", 53), timeout=timeout)
            return True
        except OSError:
            pass
        
        try:
            # Fallback: try to reach a reliable host
            socket.create_connection(("1.1.1.1", 53), timeout=timeout)
            return True
        except OSError:
            return False
    
    @staticmethod
    def check_google_translate(timeout=5):
        """Check if Google Translate service is accessible"""
        try:
            urllib.request.urlopen('https://translate.google.com', timeout=timeout)
            return True
        except (URLError, socket.timeout):
            return False
    
    @staticmethod
    def get_connectivity_status():
        """Get detailed connectivity status"""
        internet = ConnectivityChecker.check_internet()
        google_translate = False
        
        if internet:
            google_translate = ConnectivityChecker.check_google_translate()
        
        return {
            'internet': internet,
            'google_translate': google_translate,
            'status': 'online' if internet and google_translate else ('limited' if internet else 'offline')
        }

# ==================== ERROR HANDLER ====================
class TranslationErrorHandler:
    """Handle and categorize translation errors"""
    
    @staticmethod
    def categorize_error(error_msg):
        """Categorize error and provide user-friendly message"""
        error_lower = str(error_msg).lower()
        
        if 'nameerror' in error_lower or 'failed to resolve' in error_lower or 'getaddrinfo failed' in error_lower:
            return {
                'type': 'dns_error',
                'user_message': '🌐 Cannot connect to translation service. Please check your internet connection.',
                'suggestion': 'Verify that you have an active internet connection and try again.',
                'technical': str(error_msg)
            }
        elif 'max retries exceeded' in error_lower or 'connection' in error_lower:
            return {
                'type': 'connection_error',
                'user_message': '🔌 Connection to translation service failed.',
                'suggestion': 'The service might be temporarily unavailable. Please try again in a moment.',
                'technical': str(error_msg)
            }
        elif 'timeout' in error_lower:
            return {
                'type': 'timeout_error',
                'user_message': '⏱️ Translation request timed out.',
                'suggestion': 'The translation is taking too long. Try with shorter text or check your connection.',
                'technical': str(error_msg)
            }
        elif 'too many requests' in error_lower or 'rate limit' in error_lower:
            return {
                'type': 'rate_limit_error',
                'user_message': '🚫 Too many requests.',
                'suggestion': 'Please wait a moment before trying again.',
                'technical': str(error_msg)
            }
        else:
            return {
                'type': 'unknown_error',
                'user_message': '❌ Translation failed.',
                'suggestion': 'An unexpected error occurred. Please try again.',
                'technical': str(error_msg)
            }

# ==================== ROUTES ====================
@app.route("/", methods=["GET", "POST"])
def home():
    # Initialize session
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        session_data[session['session_id']] = {
            'translations': 0,
            'chars_translated': 0,
            'words_translated': 0,
            'start_time': datetime.now()
        }
    
    translated_text = ""
    source_lang = ""
    target_lang = ""
    word_count = 0
    char_count = 0
    audio_file = None
    analysis = {}
    detection_info = {}
    error_message = None
    cache_hit = False

    if request.method == "POST":
        # Rate limiting check
        if not RateLimiter.is_allowed(session['session_id']):
            error_message = "Rate limit exceeded. Please try again later."
        else:
            text = request.form["text"]
            target_lang = request.form["target"]
            
            # Validate and clean input
            is_valid, validation_msg = TextPreprocessor.validate_input(text)
            if not is_valid:
                error_message = validation_msg
            else:
                text = TextPreprocessor.clean_text(text)
                
                try:
                    # Check connectivity first
                    connectivity = ConnectivityChecker.get_connectivity_status()
                    
                    if connectivity['status'] == 'offline':
                        error_message = "🌐 No internet connection detected. Please check your network settings and try again."
                    elif connectivity['status'] == 'limited':
                        error_message = "⚠️ Internet detected but cannot reach Google Translate. It may be blocked by your firewall or proxy."
                    else:
                        # Enhanced language detection
                        detection_info = LanguageDetector.detect_with_confidence(text)
                        source_lang = detection_info['language']
                        
                        # Check cache first
                        cached_translation = TranslationCache.get(text, source_lang, target_lang)
                        if cached_translation:
                            translated_text = cached_translation
                            cache_hit = True
                        else:
                            # Translate text
                            try:
                                translated_text = GoogleTranslator(source=source_lang, target=target_lang).translate(text)
                                # Cache the result
                                TranslationCache.set(text, source_lang, target_lang, translated_text)
                            except Exception as trans_error:
                                # Handle translation-specific errors
                                error_info = TranslationErrorHandler.categorize_error(str(trans_error))
                                error_message = f"{error_info['user_message']} {error_info['suggestion']}"
                                raise
                        
                        # Only process analysis if translation succeeded
                        if translated_text and not error_message:
                            # Advanced text analysis
                            word_count = len(translated_text.split())
                            char_count = len(translated_text)
                            
                            analysis = {
                                'readability': round(TextAnalyzer.calculate_readability(text), 2),
                                'text_type': TextAnalyzer.detect_text_type(text),
                                'complexity': TextAnalyzer.get_text_complexity(text),
                                'word_frequency': TextPreprocessor.get_word_frequency(text, 5),
                                'sentence_count': len(re.findall(r'[.!?]+', text)),
                                'avg_word_length': round(sum(len(word) for word in text.split()) / max(len(text.split()), 1), 2)
                            }
                            
                            # Text-to-Speech
                            try:
                                tts_lang = target_lang if target_lang in tts_supported else "en"
                                audio_filename = f"{uuid.uuid4()}.mp3"
                                audio_path = os.path.join("static", audio_filename)
                                tts = gTTS(translated_text, lang=tts_lang)
                                tts.save(audio_path)
                                audio_file = audio_filename
                            except Exception as tts_error:
                                print(f"TTS Error: {tts_error}")
                                audio_file = None
                            
                            # Update statistics
                            StatisticsManager.update_language_stats(source_lang, target_lang)
                            
                            # Update statistics
                            StatisticsManager.update_language_stats(source_lang, target_lang)
                            
                            # Update session stats
                            session_stats = session_data[session['session_id']]
                            session_stats['translations'] += 1
                            session_stats['chars_translated'] += char_count
                            session_stats['words_translated'] += word_count
                            
                            # Add to history
                            history_entry = {
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "input": text[:100] + "..." if len(text) > 100 else text,
                                "source": source_lang,
                                "target": target_lang,
                                "output": translated_text[:100] + "..." if len(translated_text) > 100 else translated_text,
                                "words": word_count,
                                "chars": char_count,
                                "cached": cache_hit
                            }
                            history.append(history_entry)
                            
                            # Keep only last 50 entries
                            if len(history) > 50:
                                history.pop(0)
                
                except Exception as e:
                    # Detailed error handling
                    if not error_message:  # Only process if not already set
                        error_info = TranslationErrorHandler.categorize_error(str(e))
                        error_message = f"{error_info['user_message']} {error_info['suggestion']}"
                        
                        # Log technical details (in production, use proper logging)
                        print(f"Translation Error [{error_info['type']}]: {error_info['technical']}")
    
    # Get statistics
    session_stats = StatisticsManager.get_session_stats(session['session_id'])
    most_used_pairs = StatisticsManager.get_most_used_pairs(5)
    total_translations = StatisticsManager.get_total_translations()
    cache_size = len(translation_cache)
    
    # Get connectivity status for display
    connectivity = ConnectivityChecker.get_connectivity_status()
    
    return render_template(
        "index.html",
        translated_text=translated_text,
        source_lang=source_lang,
        target_lang=target_lang,
        word_count=word_count,
        char_count=char_count,
        audio_file=audio_file,
        history=list(reversed(history)),
        analysis=analysis,
        detection_info=detection_info,
        error_message=error_message,
        cache_hit=cache_hit,
        session_stats=session_stats,
        most_used_pairs=most_used_pairs,
        total_translations=total_translations,
        cache_size=cache_size,
        language_names=LANGUAGE_NAMES,
        connectivity=connectivity
    )

@app.route("/api/translate", methods=["POST"])
def api_translate():
    """API endpoint for translation"""
    data = request.get_json()
    text = data.get('text', '')
    target = data.get('target', 'en')
    
    is_valid, msg = TextPreprocessor.validate_input(text)
    if not is_valid:
        return jsonify({'error': msg}), 400
    
    try:
        source = detect(text)
        translation = GoogleTranslator(source=source, target=target).translate(text)
        return jsonify({
            'translation': translation,
            'source': source,
            'target': target,
            'success': True
        })
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@app.route("/export/<format>")
def export_history(format):
    """Export translation history"""
    if format == "json":
        filepath = os.path.join("static", "history.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        return send_file(filepath, as_attachment=True, download_name="translation_history.json")
    
    elif format == "csv":
        filepath = os.path.join("static", "history.csv")
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            if history:
                writer = csv.DictWriter(f, fieldnames=history[0].keys())
                writer.writeheader()
                writer.writerows(history)
        return send_file(filepath, as_attachment=True, download_name="translation_history.csv")
    
    return jsonify({'error': 'Invalid format'}), 400

@app.route("/clear-history", methods=["POST"])
def clear_history():
    """Clear translation history"""
    global history
    history = []
    return jsonify({'success': True})


@app.route("/check-connectivity")
def check_connectivity():
    """Check system connectivity"""
    status = ConnectivityChecker.get_connectivity_status()
    return jsonify(status)
@app.route("/stats")
def get_stats():
    """Get detailed statistics"""
    return jsonify({
        'total_translations': StatisticsManager.get_total_translations(),
        'cache_size': len(translation_cache),
        'most_used_pairs': StatisticsManager.get_most_used_pairs(10),
        'language_stats': language_stats,
        'active_sessions': len(session_data)
    })

if __name__ == "__main__":
    app.run(debug=True)