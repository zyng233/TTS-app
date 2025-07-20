import sys
import re
from pathlib import Path
from typing import Optional
from .base_tts import BaseTTS
from ..auth import AuthManager, ServiceType
from ..audio_config import generate_to_memory as generate_audio_to_memory
from ..voice import get_available_languages as voice_get_available_languages
from ..voice import get_voices_for_language as voice_get_voices_for_language
from ..monitor import get_character_stats as monitor_get_character_stats
from ..monitor import update_usage
from ..utils import setup_logger

class GoogleCloudTTS(BaseTTS):
    def __init__(self, credentials_path: Optional[Path] = None, update_callback=None):
        self.auth_manager = AuthManager()  
        self.service_type = ServiceType.GOOGLE
        self.logger = setup_logger()
        self.update_callback = update_callback
        
        try:
            self.credentials_path = credentials_path or self.auth_manager.get_credentials_path(self.service_type)
            
            self.auth_manager.validate_credentials(self.service_type, self.credentials_path)
            self.client, self.credentials = self.auth_manager.initialize_client(
                self.service_type, 
                self.credentials_path
            )
            
            if not self.client:
                raise RuntimeError("Failed to initialize TTS client. Check credentials.")
                
        except Exception as e:
            self.logger.error(f"Initialization failed: {str(e)}")
            raise RuntimeError(f"Could not initialize Google Cloud TTS: {str(e)}")
    
    def get_available_languages(self, format: str = "both"):
        return voice_get_available_languages(self.client, format=format)
    
    def get_available_voices(self, language_code: str):
        return voice_get_voices_for_language(self.client, language_code)
    
    def generate_to_memory(
        self,
        text: str,
        voice_name: Optional[str] = None,
        voice_data: Optional[dict] = None,
        audio_format: str = "MP3",
        speaking_rate: float = 1.0,
        pitch: float = 0.0,
        is_ssml: bool = False,
        effects_profile_id: Optional[list[str]] = None
    ) -> bytes:
        char_count = self.count_ssml_characters(text) if is_ssml else len(text)
        
        audio_content = generate_audio_to_memory(
            client=self.client,
            text=text,
            voice_name=voice_name,
            voice_data=voice_data,
            audio_format=audio_format,
            speaking_rate=speaking_rate,
            pitch=pitch,
            is_ssml=is_ssml,
            effects_profile_id=effects_profile_id
        )
        try:
            update_usage(char_count)
            if self.update_callback:
                self.update_callback(self.get_usage_stats())
        except Exception as e:
            self.logger.error(f"Failed to update usage: {e}")
        
        return audio_content
        
    def get_usage_stats(self):
        return monitor_get_character_stats(self)
    
    def count_ssml_characters(self, text: str) -> int:
        """
        Count characters in SSML text, ignoring all XML tags and attributes.
        Only counts text that will actually be spoken.
        """
        tag_pattern = re.compile(r'<[^>]+>')
        clean_text = tag_pattern.sub('', text)
        
        clean_text = re.sub(r'&[a-z]+;', 'X', clean_text)
        
        clean_text = ' '.join(clean_text.split())
        return len(clean_text)
       
def main():
    print("=== Google Cloud TTS Generator ===")
    try:
        tts = GoogleCloudTTS()
        return 0
    except Exception as e:
        print(f"\n❌ Error: {str(e)}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())