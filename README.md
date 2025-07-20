# Text-to-Speech (TTS) Application

![App Screenshot](/images/main_interface.png)

A cross-platform app for converting text to speech using cloud TTS services.

## ✨ Key Features

- **Text Input Box**: Type or paste any text (supports plain text and SSML)
- **Language Selection**: Choose from various supported languages
- **Voice Profiles**: Multiple voice options per language
- **Real-time Playback**: Instant audio generation and playback
- **Usage Monitoring**: Tracks character usage against service quotas
- **Optimized Audio Profiles**: Device-specific sound optimization
- **Voice Customization**: Adjustable speaking rate and pitch control

## 📋 Prerequisites

- Python 3.7+
- [Google Cloud account](https://cloud.google.com/) (for Google TTS)
- Active Google Cloud project with billing enabled

## 🚀 Quick Start

1. Download the latest release
2. Get your Google Cloud credentials (see [Detailed Setup](#detailed-setup))
3. Enable APIs (see [Detailed Setup](#detailed-setup))
4. Place credentials in `credentials/google.json`
5. Run the executable
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

### 🔑 Credentials Setup (Google Cloud TTS)

1. **Enable the TTS API**:

   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Navigate to "APIs & Services" → "Library"
   - Search for and enable these APIs:
     - **Text-to-Speech API** (essential for basic functionality)
     - **Vertex AI API** (required for Neural2/Wavenet2 voices)
     - **Cloud Storage API** (recommended for audio caching)

2. **Create a Service Account**:

   - In Cloud Console, go to "IAM & Admin" → "Service Accounts"
   - Click "Create Service Account"
   - Enter these details:
     - **Service account name**: `tts-service-account`
     - **Description**: "For Text-to-Speech application access"
   - Click "Create and Continue"

3. **Assign Required Roles**:

   - Add these essential roles:
     - **Cloud Text-to-Speech API User** (basic functionality)
     - **Vertex AI Service Agent** (for advanced voices)
     - **Storage Object Admin** (if using audio caching)
   - Click "Continue" → "Done

4. **Download Credentials**:

   - In your service account, go to "Keys" → "Add Key" → "Create new key"
   - Select JSON format and click "Create"
   - Save the downloaded file as:
     ```
     your-application-folder/credentials/google.json
     ```
   - Verify the file contains these key fields:
     ```json
     {
       "type": "service_account",
       "project_id": "your-project-id",
       "private_key_id": "...",
       "private_key": "-----BEGIN PRIVATE KEY-----\n...",
       "client_email": "...",
       "client_id": "..."
     }
     ```

## 🎮 How to Use

### 1. Enter Text

**Main Text Box** - Type or paste your content (supports both plain text and SSML)

```xml
<!-- Example using SSML -->
<speak>
  Hello <break time="0.5s"/>, welcome to <prosody rate="slow">TTS App</prosody>!
</speak>
```

### 2. Select Language & Voice

1. Language: Dropdown list (e.g. "English (US)")
2. Voice: Choose from available options (e.g. "Wavenet-D")
3. SSML Mode: Checkbox to enable/disable

### 3. Adjust Audio Preferences

| Control           | Function                    |
| ----------------- | --------------------------- |
| **Speed Slider**  | 0.25x (slow) to 4.0x (fast) |
| **Pitch Slider**  | -20 (low) to +20 (high)     |
| **Audio Profile** | Device optimization         |

### 4. Generate & Play

- Click ▶ Play to start
- Click ⏹ Stop to cancel
- Quota usage(estimated) updates automatically

> ## ⚠️ **Note**
>
> Some voice types (e.g., Chirp/Chirp3) have limitations:
>
> - ❌ SSML tags not supported
> - ❌ Pitch adjustment unavailable

## 🛠 For Developers

```bash
# Install dependencies
pip install google-cloud-texttospeech pygame
pip install -r requirements.txt

# Build executable
pyinstaller --onefile --add-data "credentials;credentials" src/main.py
```
