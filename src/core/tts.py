import sys
from pathlib import Path
from typing import Optional
from .audio_config import generate_to_memory as generate_audio_to_memory
from .auth import get_credentials_path, validate_credentials, initialize_client
from .voice import get_available_languages as voice_get_available_languages
from .voice import get_voices_for_language as voice_get_voices_for_language
from .utils import setup_logger

class TTSGenerator:
    def __init__(self, credentials_path: Optional[Path] = None):
        self.credentials_path = credentials_path or get_credentials_path()
        validate_credentials(self.credentials_path)
        self.client = initialize_client(self.credentials_path)
        if not self.client:
            raise RuntimeError("Failed to initialize TTS client. Check credentials.")
        self.logger = setup_logger()
    
    def get_available_languages(self, format: str = "both"):
        return voice_get_available_languages(self.client, format=format)
    
    def get_voices_for_language(self, language_code: str):
        return voice_get_voices_for_language(self.client, language_code)
    
    def generate_to_memory(
        self,
        text: str,
        voice_name: Optional[str] = None,
        voice_data: Optional[dict] = None,
        audio_format: str = "MP3",
        speaking_rate: float = 1.0,
        pitch: float = 0.0,
        is_ssml: bool = False
    ) -> bytes:
        return generate_audio_to_memory(
            client=self.client,
            text=text,
            voice_name=voice_name,
            voice_data=voice_data,
            audio_format=audio_format,
            speaking_rate=speaking_rate,
            pitch=pitch,
            is_ssml=is_ssml
        )
       
       
def main():
    print("=== Google Cloud TTS Generator ===")
    try:
        tts = TTSGenerator()
        return 0
    except Exception as e:
        print(f"\n❌ Error: {str(e)}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())