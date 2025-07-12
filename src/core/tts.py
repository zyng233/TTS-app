import sys
from langcodes import Language
from pathlib import Path
from typing import Optional, Dict, Union, List, Tuple
from google.cloud import texttospeech
from google.oauth2 import service_account
from google.api_core.exceptions import GoogleAPICallError
import logging

class TTSGenerator:
    
    VOICE_PRESETS = {
        "en-US-Wavenet-D": {
            "language_code": "en-US",
            "name": "en-US-Wavenet-D",
            "ssml_gender": texttospeech.SsmlVoiceGender.MALE
        },
    }
    
    AUDIO_FORMATS = {
        "MP3": texttospeech.AudioEncoding.MP3,
        "WAV": texttospeech.AudioEncoding.LINEAR16,
        "OGG": texttospeech.AudioEncoding.OGG_OPUS
    }

    def __init__(self, credentials_path: Optional[Path] = None):
        self.credentials_path = credentials_path or (
            Path(__file__).parent.parent.parent / "credentials" / "tts-key.json"
        )
        self._validate_credentials()
        self.client = self._initialize_client()
        self.logger = self._setup_logger()

    def _validate_credentials(self) -> None:
        if not self.credentials_path.exists():
            raise FileNotFoundError(
                f"Google Cloud credentials not found at {self.credentials_path}\n"
            )

    def _initialize_client(self) -> texttospeech.TextToSpeechClient:
        credentials = service_account.Credentials.from_service_account_file(
            str(self.credentials_path),
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        return texttospeech.TextToSpeechClient(credentials=credentials)

    def _setup_logger(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    
    def get_available_languages(self, format: str = "both") -> List[Union[str, Tuple[str, str]]]:
        """Get available languages in different formats"""
        try:
            response = self.client.list_voices()
            languages = set()
            for voice in response.voices:
                lang_code = voice.language_codes[0].split('-')[0]
                languages.add((lang_code, self._get_language_name(lang_code)))
            
            sorted_langs = sorted(languages, key=lambda x: x[1])
            
            if format == "name":
                return [name for (code, name) in sorted_langs]
            elif format == "code":
                return [code for (code, name) in sorted_langs]
            elif format == "full":
                return [f"{name} ({code})" for (code, name) in sorted_langs]
            else:
                return sorted_langs
                
        except GoogleAPICallError as e:
            self.logger.error(f"Failed to list languages: {e.message}")
            raise RuntimeError(f"Couldn't retrieve languages: {e.message}")
    
    def get_voices_for_language(self, language_code: str, voice_type: Optional[str] = None) -> List[Dict]:
        """Return available voices for a specific language with optional type filter"""
        try:
            response = self.client.list_voices(language_code=language_code)
            voices = [{
                'name': voice.name,
                'gender': voice.ssml_gender.name,
                'language': voice.language_codes[0],
                'sample_rate': voice.natural_sample_rate_hertz,
                'voice_type': 'Neural' if 'Neural' in voice.name else 'WaveNet'
            } for voice in response.voices]
            
            if voice_type:
                return [v for v in voices if v['voice_type'] == voice_type]
            return voices
            
        except GoogleAPICallError as e:
            self.logger.error(f"Failed to list voices: {e.message}")
            raise RuntimeError(f"Couldn't retrieve voices: {e.message}")
    
    def get_language_codes(self):
        """Return list of available language codes"""
        try:
            response = self.client.list_voices()
            return sorted({voice.language_codes[0].split('-')[0] 
                        for voice in response.voices})
        except GoogleAPICallError as e:
            self.logger.error(f"Failed to list language codes: {e.message}")
            raise RuntimeError(f"Couldn't retrieve language codes: {e.message}")
        
    def generate_to_memory(
        self,
        text: str,
        voice_name: Optional[str] = None,
        voice_data: Optional[Dict] = None,
        audio_format: str = "MP3",
        speaking_rate: float = 1.0,
        pitch: float = 0.0,
        is_ssml: bool = False
    ) -> bytes:
        """
        Generate speech and return audio binary data
        
        Args:
            text: Input text/SSML
            voice_name: Voice name (e.g., "en-US-Wavenet-D")
            voice_data: Full voice parameters (overrides voice_name)
            audio_format: Output format
            speaking_rate: Speed multiplier
            pitch: Pitch adjustment
            is_ssml: Whether input is SSML
        """
        voice_params = voice_data or {"name": voice_name or "en-US-Wavenet-D"}
        
        try:
            if audio_format.upper() not in self.AUDIO_FORMATS:
                raise ValueError(f"Unsupported audio format: {audio_format}")

            synthesis_input = (
                texttospeech.SynthesisInput(ssml=text) if is_ssml
                else texttospeech.SynthesisInput(text=text))
            
            voice = self._prepare_voice_params(voice_name, voice_params)
            
            audio_config = texttospeech.AudioConfig(
                audio_encoding=self.AUDIO_FORMATS[audio_format.upper()],
                speaking_rate=speaking_rate,
                pitch=pitch
            )

            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            return response.audio_content

        except GoogleAPICallError as e:
            raise RuntimeError(f"Google TTS API error: {e.message}") from e
        except Exception as e:
            raise RuntimeError(f"Speech generation failed: {str(e)}") from e
            
    def _prepare_voice_params(self, voice_name: str, custom_params: Optional[Dict] = None):
        """Prepare voice parameters from presets or custom values."""
        if custom_params:
            return texttospeech.VoiceSelectionParams(**custom_params)
        
        if voice_name in self.VOICE_PRESETS:
            return texttospeech.VoiceSelectionParams(**self.VOICE_PRESETS[voice_name])
        
        for lang_code in self.get_language_codes():
            voices = self.get_voices_for_language(lang_code)
            for voice in voices:
                if voice['name'] == voice_name:
                    return texttospeech.VoiceSelectionParams(
                        language_code=voice['language'],
                        name=voice['name'],
                        ssml_gender=getattr(texttospeech.SsmlVoiceGender, voice['gender'])
                    )
        parts = voice_name.split("-")
        if len(parts) >= 3:
            language_code = "-".join(parts[:2])
            return texttospeech.VoiceSelectionParams(
                language_code=language_code,
                name=voice_name,
                ssml_gender=texttospeech.SsmlVoiceGender.MALE  # Default to male
            )    
            
        return texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Wavenet-D",
            ssml_gender=texttospeech.SsmlVoiceGender.MALE
        )
        
    def _validate_audio_format(self, format_str: str) -> texttospeech.AudioEncoding:
        """Validate and return audio format enum"""
        format_str = format_str.upper()
        if format_str not in self.AUDIO_FORMATS:
            raise ValueError(
                f"Unsupported audio format: {format_str}. "
                f"Supported formats: {list(self.AUDIO_FORMATS.keys())}"
            )
        return self.AUDIO_FORMATS[format_str]
    
    def validate_language_code(self, code: str) -> bool:
        """Check if language code is available"""
        return code in [lang[0] for lang in self.get_available_languages()]
    
    @staticmethod
    def _get_language_name(lang_code: str) -> str:
        """Get language name"""
        return Language.get(lang_code).display_name()

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