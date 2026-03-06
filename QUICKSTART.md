# TransLingo Pro - Language Translation Tool

## Quick Start

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

### Access
Open your browser and go to: http://localhost:5000

## Features at a Glance

✅ 20+ Language Support
✅ Auto Language Detection
✅ Text-to-Speech
✅ Translation Cache
✅ Text Analysis (Readability, Complexity, Type)
✅ Translation History
✅ Export (JSON/CSV)
✅ Dark Mode
✅ Responsive Design
✅ Rate Limiting
✅ Session Management
✅ Statistics Dashboard
✅ API Endpoints

## Project Stats

- **Python Code**: 440+ lines of advanced logic
- **CSS**: 700+ lines of professional styling
- **HTML**: 420+ lines with modern components
- **Features**: 30+ implemented features
- **Classes**: 6 utility classes
- **API Endpoints**: 5 RESTful endpoints

## Technology Stack

**Backend:**
- Python 3.8+
- Flask 2.3+
- Deep Translator
- langdetect
- gTTS

**Frontend:**
- HTML5
- CSS3 (Custom, no frameworks!)
- Vanilla JavaScript
- Google Fonts (Inter)

## What Makes This Special?

This is not just a simple translation tool - it's a **professional-grade application** with:

1. **Advanced Python Logic** (60%+ Python workload):
   - Custom caching system with MD5 hashing
   - Text analysis algorithms (Flesch Reading Ease)
   - Rate limiting with sliding window
   - Session management
   - Statistical analysis
   - Word frequency analysis
   - Multiple utility classes

2. **Professional UI/UX**:
   - Modern, clean design
   - Dark mode support
   - Smooth animations
   - Responsive layout
   - Interactive components
   - Real-time feedback

3. **Production-Ready Features**:
   - Error handling
   - Input validation
   - Security measures
   - Performance optimization
   - Export functionality
   - API endpoints

## File Structure

```
LanguageTranslationTool/
├── app.py              # Main application (440+ lines)
├── config.py           # Configuration management
├── requirements.txt    # Dependencies
├── readme.md          # Full documentation
├── QUICKSTART.md      # This file
├── static/
│   └── style.css      # Professional styling (700+ lines)
└── templates/
    └── index.html     # Modern UI (420+ lines)
```

## Common Tasks

**Translate Text:**
1. Enter text (up to 5000 characters)
2. Select target language
3. Click "Translate Now"

**Export History:**
Click "Export JSON" or "Export CSV" in the history section

**Toggle Dark Mode:**
Click the theme toggle button in the header

**Clear History:**
Click "Clear" in the history section

## API Usage

```python
import requests

# Translate via API
response = requests.post('http://localhost:5000/api/translate',
    json={
        'text': 'Hello World',
        'target': 'fr'
    }
)
print(response.json())
```

## Need Help?

Check the full [readme.md](readme.md) for detailed documentation.

---

**Happy Translating! 🌐✨**
