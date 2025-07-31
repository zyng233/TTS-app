# Text-to-Speech (TTS) Application

A cross-platform app for converting text to speech using TTS services like Google Cloud and ElevenLabs.

![Google Cloud TTS UI](/images/google_interface.png)
![ElevenLabs TTS UI](/images/elevenlabs_interface.png)

## ✨ Key Features

- **Multi-Service Switching**: Seamlessly switch between Google Cloud and ElevenLabs
- **Text Input Box**: Type or paste any text (Google Cloud supports SSML)
- **Language & Voice Selection**: Wide support for multiple languages and region-specific voices
- **Usage Monitoring**: Tracks character usage against service quotas
- **Advanced Voice Controls**:
  - **Google Cloud**: Control speaking rate, pitch, audio profiles
  - **ElevenLabs**: Control stability, similarity boost, style, speed, speaker boost
- **Real-time Playback**: Instant audio generation and playback
- **Audio Download**: Save generated speech audio in multiple formats

## 📋 Prerequisites

- Python 3.10+ (Recommended)
- Google Cloud TTS
  - [Google Cloud account](https://cloud.google.com/)
  - Active Google Cloud project with billing enabled
  - Cloud Text-to-Speech API enabled
  - Service account credentials JSON file
- ElevenLabs TTS
  - [ElevenLsbs account](https://elevenlabs.io/)
  - API key (available in your profile settings)
  - At least one voice configured in your account

## 🚀 Quick Start

1. Download the latest release
2. Add your credentials:
   - Get your Google Cloud credential (see [Credentials Setup For Google Cloud](#Credentials-Setup-For-Google-Cloud-TTS))
   - Get your ElevenLabs credential (see [Credentials Setup For ElevenLabs](#Credentials-Setup-For-ElevenLabs-TTS))
3. Run the executable
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

## ⚙️ Detailed Setup

### 🔑 Credentials Setup For Google Cloud TTS

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

### 🔐 Credentials Setup For ElevenLabs TTS

1. **Create an ElevenLabs Account**

   - Visit [https://www.elevenlabs.io](https://www.elevenlabs.io)
   - Sign up or log in to your account

2. **Generate Your API Key**

   - Click your **profile icon** → **Profile**
   - Scroll to the **"API Keys"** section
   - Click **"Create API Key"**, enter a name (e.g., `TTS App`)
   - Under **"Restrict Key"**, make sure to give access to:
     - ✅ Text to Speech
     - ✅ Voices
     - ✅ Voice Generation
   - Click **"Create"**

3. **Save the API Key Locally**
   - Create a file at:
     ```
     credentials/elevenlabs.json
     ```
   - Paste the following content into the file, replacing `YOUR_API_KEY` with your actual key:
     ```json
     {
       "api_key": "YOUR_API_KEY"
     }
     ```

## 🎮 How to Use

### 1. Select TTS Service

Use the service switcher dropdown in the top control bar to switch between providers:

![Service Switcher](/images/service_switcher.png)

- **Google Cloud TTS**: Best for accurate pronunciations and SSML support
- **ElevenLabs**: Best for natural-sounding voices and emotional range

> 💡 The UI will automatically reconfigure to show the appropriate controls for your selected service.

### 2. Enter Text

**Main Text Box** - Type or paste your content

```xml
<!-- Example using SSML -->
<speak>
  Hello <break time="0.5s"/>, welcome to <prosody rate="slow">TTS App</prosody>!
</speak>
```

### 3. Select Language & Voice

Depending on the selected TTS service (Google Cloud or ElevenLabs), the language and voice controls will adjust accordingly.

#### 🟦 Google Cloud TTS

- **Language**: Select from supported languages (e.g., English, Japanese, German)
- **Voice**: Choose standard, Wavenet, or Neural2 voices

  ![Google Voice Settings](/images/google_voice_selection.png)

- **Pitch & Speed Controls**: Adjustable via sliders
- **Audio Profile**: Select device-optimized profiles (e.g., wearable-class-device, telephony-class-application)
- **SSML**: Fully supported (including `<prosody>`, `<break>`, etc.)

  🔗 [Google TTS SSML Guide](https://cloud.google.com/text-to-speech/docs/ssml)

#### 🟨 ElevenLabs

- **Model Selection**: Choose from available voice models (e.g., eleven_multilingual_v2)
- **Language**: Select from supported languages based on selected model (e.g., English, Japanese, German)
- **Voice**: Choose from a list of high-quality voices

  ![ElevenLabs Voice Settings](/images/elevenlabs_voice_selection.png)

- **Custom Controls**:
  - **Stability**: Controls how stable the voice remains across generations
  - **Similarity Boost**: Increases similarity to the base voice
  - **Style**: Expressiveness or tone of delivery
  - **Speaker Boost**: Enhances speaker clarity and loudness
  - **Speed**: Adjustable in supported voices

### 4. Adjust Audio Preferences

You can choose the format in which to download the generated audio. Available options depend on the selected TTS service:

#### 🟦 Google Cloud TTS

- **Supported Formats**: `MP3`, `LINEAR16` (WAV), `OGG_OPUS`
- **Default Format**: `MP3`
- ✅ SSML-compatible downloads supported

#### 🟨 ElevenLabs

- **Supported Formats**: `MP3`, `PCM`, `ULAW`
- **Default Format**: `MP3`
- 🔧 Advanced voices may take slightly longer to generate

### 5. Generate & Play

- Click ▶ Play to start
- Click ⏹ Stop to cancel
- Click ⏯ Pause/Resume to toggle playback
- Click ↓ Download to save the previous played audio in your chosen format
- Character usage updates automatically

> ## ⚠️ **Note**
>
> Some Google Cloud TTS voice types (e.g., **Chirp**, **Chirp3**) have limitations:
>
> - ❌ SSML tags not supported
> - ❌ Pitch adjustment unavailable
> - 🚫 API usage statistics are currently **not available**
>
> The **ElevenLabs** service in this app currently supports only two models:
>
> - 🧠 **Multilingual v2**
> - ⚡ **Turbo v2**
>
> These models may:
>
> - ⏳ Take slightly longer to generate audio due to model complexity
> - 🔁 Occasionally trigger retry logic if the API response is delayed
>
> 🕒 **API usage statistics** for ElevenLabs may take a few seconds to reflect recent activity.

## 🛠 For Developers

```bash
# Install dependencies
pip install google-cloud-texttospeech pygame
pip install -r requirements.txt

# Build executable
pyinstaller --onefile --add-data "credentials;credentials" src/main.py
```
