# Text-to-Speech (TTS) Application

A cross-platform app for converting text to speech using cloud TTS services.

## Setup Instructions

### 1. Prerequisites
- Python 3.7+
- [Google Cloud account](https://cloud.google.com/) (for Google TTS)

### 2. Credentials Setup (Google Cloud TTS)

#### For Google Cloud TTS:
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

4. **Place the Credentials File**:
    - Place the JSON file as `credentials.json` in credentials folder

### 3. Run the executable

1. Install dependencies:
```bash
pip install google-cloud-texttospeech pygame tkinter

2. Run the app:
```bash
python src/main.py