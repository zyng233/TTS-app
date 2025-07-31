from google.cloud import texttospeech
from google.api_core.exceptions import GoogleAPICallError
from typing import Optional, Dict, Union, List
from enum import Enum
from dataclasses import dataclass
from .voice import GoogleVoiceManager

class GoogleAudioFormat(str, Enum):
    """Supported Google TTS audio formats"""
    MP3 = "MP3"
    WAV = "WAV"
    OGG = "OGG"

class GoogleVoiceGender(str, Enum):
    """Supported voice genders"""
    MALE = "MALE"
    FEMALE = "FEMALE"
    NEUTRAL = "NEUTRAL"

@dataclass
class GoogleVoiceParams:
    """Structured voice parameters container"""
    name: str = "en-US-Wavenet-D"
    language_code: str = "en-US"
    gender: GoogleVoiceGender = GoogleVoiceGender.MALE

class GoogleAudioConfig:
    """Handle Google Cloud TTS audio generation with validation"""
    
    FORMAT_MAPPING = {
        GoogleAudioFormat.MP3: texttospeech.AudioEncoding.MP3,
        GoogleAudioFormat.WAV: texttospeech.AudioEncoding.LINEAR16,
        GoogleAudioFormat.OGG: texttospeech.AudioEncoding.OGG_OPUS
    }
    
    def __init__(self, client):
        self.client = client
        self.voice_manager = GoogleVoiceManager(client)
        
    def generate_to_memory(
        self,
        text: str,
        voice_name: Optional[str] = None,
        voice_data: Optional[Union[Dict, GoogleVoiceParams]] = None,
        audio_format: Union[str, GoogleAudioFormat] = GoogleAudioFormat.MP3,
        speaking_rate: float = 1.0,
        pitch: float = 0.0,
        is_ssml: bool = False,
        effects_profile_id: Optional[list[str]] = None
    ) -> bytes:
        """
        Generate speech and return audio binary data
        
        Args:
            text: Input text/SSML
            voice_name: Voice name (e.g., "en-US-Wavenet-D")
            voice_data: Voice parameters (dict or GoogleVoiceParams)
            audio_format: Output format (str or GoogleAudioFormat enum)
            speaking_rate: 0.25-4.0 (speed multiplier)
            pitch: -20.0-20.0 (pitch adjustment)
            is_ssml: Whether input is SSML
            effects_profile_id: Audio effects profiles
        """
        try:
            fmt = self._validate_format(audio_format)
            voice = self._prepare_voice_params(voice_name, voice_data)
            audio_config = self._prepare_audio_config(
                fmt, speaking_rate, pitch, effects_profile_id
            )

            synthesis_input = (
                texttospeech.SynthesisInput(ssml=text) if is_ssml
                else texttospeech.SynthesisInput(text=text)
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

    def _prepare_voice_params(
        self,
        voice_name: Optional[str],
        voice_data: Optional[Union[Dict, GoogleVoiceParams]]
    ) -> texttospeech.VoiceSelectionParams:
        """Prepare validated voice parameters"""
        if voice_data:
            if isinstance(voice_data, GoogleVoiceParams):
                return texttospeech.VoiceSelectionParams(
                    language_code=voice_data.language_code,
                    name=voice_data.name,
                    ssml_gender=getattr(
                        texttospeech.SsmlVoiceGender, 
                        voice_data.gender.value
                    )
                )
            return texttospeech.VoiceSelectionParams(**voice_data)
        
        if voice_name:
            for lang_code in self.voice_manager.get_language_codes():
                voices = self.voice_manager.get_voices_for_language(lang_code)
                for voice in voices:
                    if voice['name'] == voice_name:
                        return texttospeech.VoiceSelectionParams(
                            language_code=voice['language'],
                            name=voice['name'],
                            ssml_gender=getattr(
                                texttospeech.SsmlVoiceGender, 
                                voice['gender']
                            )
                        )
        
        return texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Wavenet-D",
            ssml_gender=texttospeech.SsmlVoiceGender.MALE
        )

    def _prepare_audio_config(
        self,
        audio_format: GoogleAudioFormat,
        speaking_rate: float,
        pitch: float,
        effects_profile_id: Optional[list[str]]
    ) -> texttospeech.AudioConfig:
        """Prepare validated audio configuration"""
        return texttospeech.AudioConfig(
            audio_encoding=self.FORMAT_MAPPING[audio_format],
            speaking_rate=self._validate_range(speaking_rate, "speaking_rate", 0.25, 4.0),
            pitch=self._validate_range(pitch, "pitch", -20.0, 20.0),
            effects_profile_id=effects_profile_id or []
        )

    @staticmethod
    def _validate_format(fmt: Union[str, GoogleAudioFormat]) -> GoogleAudioFormat:
        """Validate and normalize audio format"""
        if isinstance(fmt, GoogleAudioFormat):
            return fmt
        try:
            return GoogleAudioFormat(fmt.upper())
        except ValueError:
            raise ValueError(
                f"Unsupported audio format: {fmt}. "
                f"Supported: {[f.value for f in GoogleAudioFormat]}"
            )

    @staticmethod
    def _validate_range(value: float, param_name: str, min_val: float, max_val: float) -> float:
        """Validate a numeric parameter is within range"""
        if not min_val <= value <= max_val:
            raise ValueError(
                f"{param_name} must be between {min_val} and {max_val}, got {value}"
            )
        return value
    
    @classmethod
    def get_supported_formats(cls) -> List[str]:
        """Returns the list of supported audio formats"""
        return [fmt.value for fmt in GoogleAudioFormat]