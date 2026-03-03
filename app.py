from flask import Flask, render_template, request
from deep_translator import GoogleTranslator
from langdetect import detect
from gtts import gTTS
import os
import uuid

app = Flask(__name__)

# Store translation history in memory
history = []

# Supported TTS languages
tts_supported = ["en", "fr", "ta"]

@app.route("/", methods=["GET", "POST"])
def home():
    translated_text = ""
    source_lang = ""
    target_lang = ""
    word_count = 0
    char_count = 0
    audio_file = None

    if request.method == "POST":
        text = request.form["text"]
        target_lang = request.form["target"]

        # Auto-detect source language
        try:
            source_lang = detect(text)
        except:
            source_lang = "en"

        # Translate text
        translated_text = GoogleTranslator(source=source_lang, target=target_lang).translate(text)

        # Word and character count
        word_count = len(translated_text.split())
        char_count = len(translated_text)

        # Text-to-Speech (fallback to English if not supported)
        tts_lang = target_lang if target_lang in tts_supported else "en"
        audio_filename = f"{uuid.uuid4()}.mp3"
        audio_path = os.path.join("static", audio_filename)
        tts = gTTS(translated_text, lang=tts_lang)
        tts.save(audio_path)
        audio_file = audio_filename

        # Add to history
        history.append({
            "input": text,
            "source": source_lang,
            "target": target_lang,
            "output": translated_text,
            "words": word_count,
            "chars": char_count
        })

    return render_template(
        "index.html",
        translated_text=translated_text,
        source_lang=source_lang,
        target_lang=target_lang,
        word_count=word_count,
        char_count=char_count,
        audio_file=audio_file,
        history=reversed(history)  # show latest first
    )

if __name__ == "__main__":
    app.run(debug=True)