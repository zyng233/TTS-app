import requests
from typing import Dict, Optional, Union, List
from dataclasses import dataclass
from enum import Enum
from .voice import ElevenLabsVoiceManager

class ElevenLabsModel(str, Enum):
    """Supported ElevenLabs models"""
    MULTILINGUAL_V2 = "eleven_multilingual_v2"
    TURBO_V2 = "eleven_turbo_v2"

class ElevenLabsAudioFormat(str, Enum):
    """Supported audio output formats"""
    MP3 = "MP3"
    PCM = "PCM"
    ULAW = "ULAW"
    
@dataclass
class ElevenLabsVoiceParams:
    """Structured voice settings container"""
    voice_id: str = "21m00Tcm4TlvDq8ikWAM"
    model: ElevenLabsModel = ElevenLabsModel.MULTILINGUAL_V2
    stability: float = 0.5
    similarity_boost: float = 0.75
    style: Optional[float] = None
    speaker_boost: bool = True
    speed: Optional[float] = None
    
class ElevenLabsAudioConfig:
    """Handle ElevenLabs-specific audio generation parameters"""
    
    API_URL = "https://api.elevenlabs.io/v1"
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.voice_manager = ElevenLabsVoiceManager(api_key)

    def generate_to_memory(
        self,
        text: str,
        voice_data: Optional[Union[Dict, ElevenLabsVoiceParams]] = None,
        audio_format: Union[str, ElevenLabsAudioFormat] = ElevenLabsAudioFormat.MP3
    ) -> bytes:
        """Generate speech from ElevenLabs API and return audio bytes."""
        try:
            fmt = self._validate_format(audio_format)
            voice_params = self._prepare_voice_params(voice_data)
            model = voice_data.get("model", ElevenLabsModel.MULTILINGUAL_V2.value)
            
            headers = {
                "xi-api-key": self.api_key,
                "Content-Type": "application/json"
            }

            body = {
                "text": text,
                "model_id": model,
                "voice_settings": {
                    "stability": self._validate_range(voice_params.stability, "stability", 0, 1),
                    "similarity_boost": self._validate_range(voice_params.similarity_boost, "similarity_boost", 0, 1),
                    "speaker_boost": bool(voice_params.speaker_boost),
                }
            }

            if voice_params.style is not None:
                body["voice_settings"]["style"] = self._validate_range(voice_params.style, "style", 0, 1)
            if voice_params.speed is not None:
                body["voice_settings"]["speed"] = self._validate_range(voice_params.speed, "speed", 0.5, 2.0)

            endpoint = f"{self.API_URL}/text-to-speech/{voice_params.voice_id}"
            params = {"audio_format": fmt.value.lower()}

            response = requests.post(
                url=endpoint,
                headers=headers,
                params=params,
                json=body
            )
            response.raise_for_status()
            return response.content

        except requests.RequestException as e:
            raise RuntimeError(f"ElevenLabs TTS generation failed: {str(e)}") from e

    def _prepare_voice_params(
        self, voice_data: Optional[Union[Dict, ElevenLabsVoiceParams]]
    ) -> ElevenLabsVoiceParams:
        """Normalize and validate voice params."""
        if isinstance(voice_data, ElevenLabsVoiceParams):
            return voice_data
        elif isinstance(voice_data, dict):
            return ElevenLabsVoiceParams(
                voice_id=voice_data.get("voice_id", "21m00Tcm4TlvDq8ikWAM"),
                model=self._validate_model(voice_data.get("model", "eleven_monolingual_v1")),
                stability=voice_data.get("stability", 0.5),
                similarity_boost=voice_data.get("similarity_boost", 0.75),
                style=voice_data.get("style"),
                speaker_boost=voice_data.get("speaker_boost", True),
                speed=voice_data.get("speed")
            )
        else:
            return ElevenLabsVoiceParams()
        
    @staticmethod
    def _validate_model(model: Union[str, ElevenLabsModel]) -> ElevenLabsModel:
        """Validate and return normalized model enum"""
        if isinstance(model, ElevenLabsModel):
            return model
        print(model)
        try:
            return ElevenLabsModel(model.lower())
        except ValueError:
            raise ValueError(
                f"Unsupported ElevenLabs model: {model}. "
                f"Supported: {[m.value for m in ElevenLabsModel]}"
            )
    
    @staticmethod
    def _validate_format(audio_format: Union[str, ElevenLabsAudioFormat]) -> ElevenLabsAudioFormat:
        """Validate and return normalized audio format enum"""
        if isinstance(audio_format, ElevenLabsAudioFormat):
            return audio_format
            
        try:
            return ElevenLabsAudioFormat(audio_format.upper())
        except ValueError:
            raise ValueError(
                f"Unsupported ElevenLabs audio format: {audio_format}. "
                f"Supported: {[f.value for f in ElevenLabsAudioFormat]}"
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
        return [fmt.value for fmt in ElevenLabsAudioFormat]
