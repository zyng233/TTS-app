# Text-to-Speech (TTS) Application

A cross-platform app for converting text to speech using cloud TTS services.

## ✨ Key Features

- **Text Input Box**: Type or paste any text (supports plain text and SSML)
- **Language Selection**: Choose from various supported languages
- **Voice Profiles**: Multiple voice options per language
- **Real-time Playback**: Instant audio generation and playback
- **Play/Stop Controls**: Simple audio control buttons

## 📋 Prerequisites

- Python 3.7+
- [Google Cloud account](https://cloud.google.com/) (for Google TTS)
- Active Google Cloud project with billing enabled

## 🚀 Quick Start

1. Download the latest release
2. Get your Google Cloud credentials (see [Detailed Setup](#detailed-setup))
3. Place credentials in `credentials/credentials.json`
4. Run the executable
   - **Windows**:
     ```bash
     .\TTS_App_Windows.exe
     ```
   - **Mac**:
     ```bash
     chmod +x TTS_App_macOS
     ./TTS_App_macOS
     ```
   - **Linux**:
     ```bash
     chmod +x TTS_App_Linux
     ./TTS_App_Linux
     ```

## Detailed Setup

## 🔑 Credentials Setup (Google Cloud TTS)

1. **Enable the TTS API**:

   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Navigate to "APIs & Services" → "Library"
   - Search for "Text-to-Speech API" and enable it

2. **Create a Service Account**:

   - In Cloud Console, go to "IAM & Admin" → "Service Accounts"
   - Click "Create Service Account"
   - Add the "Cloud Text-to-Speech API User" role

3. **Download Credentials**:

   - In your service account, go to "Keys" → "Add Key" → "Create new key"
   - Select JSON format and download the file
   - Save as `credentials/credentials.json` in the application directory

## 🎮 How to Use

### 1. Enter Text

Type or paste your text into the main text box:

```xml
<!-- Example using SSML -->
<speak>
  Hello <break time="0.5s"/>, welcome to <prosody rate="slow">TTS App</prosody>!
</speak>
```

### 2. Select Language & Voice

1. Choose a language from the dropdown (e.g., "English (US)")
2. Select your preferred voice (e.g., "Wavenet-D")

### 3. Control Playback

| Button      | Action                     |
| ----------- | -------------------------- |
| ▶️ **Play** | Generates and plays audio  |
| ⏹ **Stop**  | Immediately stops playback |

### 4. Advanced Options

- **SSML MODE**: Check to enable SSML tags

## 🛠 For Developers

```bash
# Install dependencies
pip install google-cloud-texttospeech pygame

# Build executable
pyinstaller --onefile --add-data "credentials;credentials" src/main.py
```
