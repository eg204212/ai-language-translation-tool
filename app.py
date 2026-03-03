from flask import Flask, render_template, request
from deep_translator import GoogleTranslator
from gtts import gTTS
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    translated_text = ""

    if request.method == "POST":
        text = request.form["text"]
        source = request.form["source"]
        target = request.form["target"]

        # Translation
        translated_text = GoogleTranslator(
            source=source,
            target=target
        ).translate(text)

        # Text-to-Speech (only if translation exists)
        if translated_text:
            tts = gTTS(text=translated_text, lang="en")
            tts.save("static/output.mp3")

    return render_template("index.html", translated_text=translated_text)

if __name__ == "__main__":
    app.run(debug=True)