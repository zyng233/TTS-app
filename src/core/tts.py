import sys
from pathlib import Path
from typing import Optional, Dict, Union
from google.cloud import texttospeech
from google.oauth2 import service_account
from google.api_core.exceptions import GoogleAPICallError

class TTSGenerator:

    VOICE_PRESETS = {
        "en-US-Wavenet-D": {
            "language_code": "en-US",
            "name": "en-US-Wavenet-D",
            "ssml_gender": texttospeech.SsmlVoiceGender.MALE
        },
        "en-US-Neural2-J": {
            "language_code": "en-US",
            "name": "en-US-Neural2-J",
            "ssml_gender": texttospeech.SsmlVoiceGender.FEMALE
        }
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

    def list_voices(self, language_code: str = None) -> list:
        try:
            response = self.client.list_voices(language_code=language_code)
            return [voice.name for voice in response.voices]
        except GoogleAPICallError as e:
            raise RuntimeError(f"Failed to list voices: {e.message}") from e

    def generate_speech(
        self,
        text: str,
        output_file: Union[str, Path] = "output.mp3",
        voice_name: str = "en-US-Wavenet-D",
        audio_format: str = "MP3",
        speaking_rate: float = 1.0,
        pitch: float = 0.0,
        is_ssml: bool = False,
        voice_params: Optional[Dict] = None
    ) -> Path:
        """
        Convert text/SSML to speech audio file with enhanced parameters.
        
        Args:
            text: Input text or SSML content
            output_file: Output filename (default: "output.mp3")
            voice_name: Name of the voice to use (default: "en-US-Wavenet-D")
            audio_format: Output format (MP3, WAV, OGG) (default: "MP3")
            speaking_rate: Speaking speed multiplier (default: 1.0)
            pitch: Pitch adjustment (-20.0 to 20.0) (default: 0.0)
            is_ssml: Whether input is SSML markup (default: False)
            voice_params: Custom voice parameters (optional)
            
        Returns:
            Path to the generated audio file
            
        Raises:
            RuntimeError: If speech generation fails
            ValueError: If invalid parameters are provided
        """
        try:
            if audio_format.upper() not in self.AUDIO_FORMATS:
                raise ValueError(
                    f"Unsupported audio format: {audio_format}. "
                    f"Supported formats: {list(self.AUDIO_FORMATS.keys())}"
                )

            synthesis_input = (
                texttospeech.SynthesisInput(ssml=text) if is_ssml
                else texttospeech.SynthesisInput(text=text)
            )

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

            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, "wb") as out:
                out.write(response.audio_content)
            
            return output_path

        except GoogleAPICallError as e:
            raise RuntimeError(f"Google TTS API error: {e.message}") from e
        except Exception as e:
            raise RuntimeError(f"Speech generation failed: {str(e)}") from e
    
    def generate_to_memory(
        self,
        text: str,
        voice_name: str = "en-US-Wavenet-D",
        audio_format: str = "MP3",
        speaking_rate: float = 1.0,
        pitch: float = 0.0,
        is_ssml: bool = False,
        voice_params: Optional[Dict] = None
    ) -> bytes:
        """
        Generate speech and return audio binary data
        
        Args:
            text: Input text/SSML
            voice_name: Voice to use
            audio_format: Output format
            speaking_rate: Speed multiplier
            pitch: Pitch adjustment
            is_ssml: Whether input is SSML
            voice_params: Custom voice params
            
        Returns:
            bytes: Audio data in specified format
        """
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
        
        parts = voice_name.split("-")
        if len(parts) >= 3:
            language_code = "-".join(parts[:2])
            return texttospeech.VoiceSelectionParams(
                language_code=language_code,
                name=voice_name,
                ssml_gender=self._guess_gender(voice_name)
            )
        
        return texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Wavenet-D",
            ssml_gender=texttospeech.SsmlVoiceGender.MALE
        )

    @staticmethod
    def _guess_gender(voice_name: str) -> texttospeech.SsmlVoiceGender:
        """Guess gender from voice name."""
        voice_name = voice_name.lower()
        if "female" in voice_name or "-a" in voice_name or "-c" in voice_name or "-f" in voice_name:
            return texttospeech.SsmlVoiceGender.FEMALE
        return texttospeech.SsmlVoiceGender.MALE


def main():
    print("=== Google Cloud TTS Generator ===")
    
    try:
        tts = TTSGenerator()
        
        output_path = tts.generate_speech(
            text="Hello, this is a test of the enhanced TTS system.",
            output_file="enhanced_output.mp3",
            voice_name="en-US-Neural2-J",
            audio_format="MP3",
            speaking_rate=1.1,
            pitch=2.0
        )
        
        print(f"\n✅ Successfully generated audio at: {output_path}")
        return 0
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())