# 🔧 Troubleshooting Guide - TransLingo Pro

## Common Connection Errors

### 1. DNS Resolution Error (Network Error)

**Error Message:**
```
Translation error: HTTPSConnectionPool(host='translate.google.com', port=443): Max retries exceeded with url: /m?tl=en&sl=nl&q=school (Caused by NameResolutionError("Failed to resolve 'translate.google.com'"))
```

**What it means:**
Your computer cannot connect to Google's translation service. This is typically a network connectivity issue.

**Solutions:**

#### Option 1: Check Internet Connection
```bash
# On Windows PowerShell
Test-NetConnection google.com -Port 443

# Or simply
ping google.com
```

If ping fails, your internet connection is down.

**Fix:**
- Check WiFi/Ethernet connection
- Restart your router
- Try a different network
- Contact your ISP

#### Option 2: Check DNS Settings
Windows DNS might be corrupted or slow.

**Fix - Flush DNS Cache:**
```powershell
# Run PowerShell as Administrator
ipconfig /flushdns
ipconfig /release
ipconfig /renew
```

**Fix - Use Google DNS:**
1. Open Network Settings
2. Change adapter settings
3. Right-click your connection → Properties
4. Select "Internet Protocol Version 4 (TCP/IPv4)"
5. Click Properties
6. Use these DNS servers:
   - Preferred DNS: `8.8.8.8`
   - Alternate DNS: `8.8.4.4`

#### Option 3: Check Firewall/Antivirus
Your firewall might be blocking the connection.

**Fix:**
1. Windows Defender Firewall → Allow an app
2. Add Python to allowed apps
3. Temporarily disable antivirus and test

#### Option 4: Check Proxy Settings
If you're behind a corporate proxy:

```python
# Add to app.py after imports
import os
os.environ['HTTP_PROXY'] = 'http://your-proxy:port'
os.environ['HTTPS_PROXY'] = 'http://your-proxy:port'
```

#### Option 5: Use VPN
Sometimes ISPs or countries block Google services.

**Fix:**
- Use a reputable VPN service
- Connect to a server in a different country
- Try the translation again

---

### 2. Timeout Error

**Error Message:**
```
⏱️ Translation request timed out.
```

**Causes:**
- Slow internet connection
- Google Translate servers are overloaded
- Text is too long

**Solutions:**
1. **Reduce text size** - Try translating smaller chunks
2. **Check internet speed** - Run a speed test
3. **Wait and retry** - Service might be temporarily slow
4. **Use cached translations** - If you translated before, it should be instant

---

### 3. Rate Limit Error

**Error Message:**
```
🚫 Too many requests. Please wait a moment before trying again.
```

**Causes:**
- Made too many translations in short time (50+ per hour)
- Google's rate limiting

**Solutions:**
1. **Wait 5-10 minutes** before trying again
2. **Use cache** - Already translated text is instant
3. **Clear app cache** if rate limit persists

---

### 4. Service Unavailable

**Error Message:**
```
⚠️ Internet detected but cannot reach Google Translate.
```

**Causes:**
- Google Translate service is down
- Your network blocks Google services
- Firewall/proxy restrictions

**Solutions:**

#### Check if Google Translate is Down:
Visit: https://downdetector.com/status/google-translate/

#### Use Alternative Translation Service:
You can modify the code to use a different translation API:

```python
# In app.py, add alternative translator
from deep_translator import MyMemoryTranslator

# Use in place of GoogleTranslator
translated_text = MyMemoryTranslator(source=source_lang, target=target_lang).translate(text)
```

---

## Built-in Troubleshooting Features

### Connectivity Checker
The app now includes automatic connectivity checking:

1. **Status Indicator** in header shows:
   - 🟢 **Online** - Everything working
   - 🟡 **Limited** - Internet OK, Google Translate blocked
   - 🔴 **Offline** - No internet connection

2. **Check Connection Button** - Click to manually test connectivity

3. **Auto-refresh** - Status updates every 30 seconds

### API Endpoint
Check connectivity programmatically:

```bash
# Using PowerShell
Invoke-RestMethod -Uri "http://localhost:5000/check-connectivity"
```

Response:
```json
{
  "internet": true,
  "google_translate": true,
  "status": "online"
}
```

---

## Error Handler Features

The app now automatically:
1. **Detects connection issues** before attempting translation
2. **Provides user-friendly messages** instead of technical errors
3. **Suggests fixes** based on error type
4. **Caches translations** to work even with intermittent connectivity

---

## Testing Connectivity

### Test Internet Connection:
```powershell
# Test general internet
Test-Connection google.com

# Test translation service specifically
Test-NetConnection translate.google.com -Port 443
```

### Test from Python:
```python
import socket
import urllib.request

# Test DNS
try:
    socket.create_connection(("8.8.8.8", 53), timeout=3)
    print("✓ DNS working")
except:
    print("✗ DNS failed")

# Test Google Translate
try:
    urllib.request.urlopen('https://translate.google.com', timeout=5)
    print("✓ Google Translate accessible")
except:
    print("✗ Google Translate blocked")
```

---

## Performance Tips

### 1. Use Translation Cache
- Already translated text is instant
- Cache lasts 1 hour
- No internet needed for cached translations

### 2. Translate in Batches
- Don't translate same text multiple times
- Use "Copy" button to save translations

### 3. Monitor Status
- Watch connectivity indicator
- Don't translate when offline
- Wait for "Online" status

---

## Advanced Solutions

### Work Offline with Cache
If you have intermittent connectivity:

1. Translate everything you need in one session
2. Cache stores up to 50 recent translations
3. Export history for later reference
4. Use cached translations when offline

### Setup Local Translation (Advanced)
For offline translation, you can install:

```bash
pip install argostranslate
```

Then modify app.py to use local models (requires additional setup).

---

## Still Having Issues?

### Diagnostic Checklist:
- [ ] Internet connection working? (Test: visit google.com)
- [ ] DNS resolving? (Run: `nslookup translate.google.com`)
- [ ] Firewall allowing Python? (Check Windows Firewall)
- [ ] Using correct Python environment? (Same venv as installation)
- [ ] Dependencies installed? (Run: `pip install -r requirements.txt`)
- [ ] Latest code version? (Check for updates)

### Get Detailed Error Info:
The app logs technical details to console. Check terminal for:
```
Translation Error [dns_error]: <technical details>
```

### Report Issue:
If none of these solutions work, please report with:
1. Full error message from browser
2. Console output from terminal
3. Connectivity test results
4. Your network setup (home/corporate/VPN)

---

## Quick Reference

| Error Type | Quick Fix |
|------------|-----------|
| DNS Error | Flush DNS, use Google DNS (8.8.8.8) |
| Connection Error | Check internet, restart router |
| Timeout | Reduce text size, check speed |
| Rate Limit | Wait 10 minutes |
| Service Down | Check downdetector.com |

---

**Last Updated:** March 5, 2026

For more information, see the main [readme.md](readme.md)
