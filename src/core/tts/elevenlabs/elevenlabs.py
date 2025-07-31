from typing import Dict, Optional, Union, List, Tuple
from ..base_tts import BaseTTS
from ...auth import AuthManager
from core.tts.service_types import TTSService
from ...utils import setup_logger
from .voice import ElevenLabsVoiceManager
from .audio_config import ElevenLabsAudioConfig
from .monitor import ElevenLabsUsageMonitor

class ElevenLabsTTS(BaseTTS):
    BASE_URL = "https://api.elevenlabs.io/v1"
    
    def __init__(self, api_key: str, update_callback=None, auth_manager=None):
        self.auth_manager = auth_manager or AuthManager() 
        self.service_type = TTSService.ELEVENLABS
        self.logger = setup_logger()
        self.update_callback = update_callback
        self.character_count = 0
        
        try:
            self.api_key = api_key or self.auth_manager.get_api_key(self.service_type)

            if not self.api_key:
                raise RuntimeError("No API key provided for ElevenLabs")
            
            self.voice_manager = ElevenLabsVoiceManager(self.api_key)
            self.audio_config = ElevenLabsAudioConfig(self.api_key)
            self.usage_monitor = ElevenLabsUsageMonitor(self.api_key)
            
            self.get_usage_stats()
        except Exception as e:
            self.logger.error(f"Initialization failed: {str(e)}")
            raise RuntimeError(f"Could not initialize ElevenLabs TTS: {str(e)}")

    def get_available_languages(self, model: Optional[str], format: str = "both") -> List[Union[str, Tuple[str, str]]]:
        """Delegate to voice manager"""
        return self.voice_manager.get_available_languages(model, format)
    
    def get_available_voices(self, language_code: Optional[str] = None) -> List[Dict]:
        """Delegate to voice manager"""
        return self.voice_manager.get_voices_for_language(language_code)
    
    def generate_to_memory(
        self,
        text: str,
        voice_data: Optional[Dict] = None,
        audio_format: str = "MP3",
        stability: float = 0.5,
        similarity_boost: float = 0.75,
        speed: Optional[float] = 1.0,
        style: Optional[float] = 0.0,
        speaker_boost: Optional[bool] = False,
        **kwargs
    ) -> bytes:
        char_count = len(text)
        voice_data = {
            "voice_id": voice_data.get('voice_id' or "21m00Tcm4TlvDq8ikWAM"),
            "model": voice_data.get("model", "eleven_monolingual_v1"),
            "stability": stability,
            "similarity_boost": similarity_boost,
            "speed": speed,
            "style": style,
            "speaker_boost": speaker_boost,
            **kwargs
        }
        audio_content = self.audio_config.generate_to_memory(
            text=text,
            voice_data=voice_data,
            audio_format=audio_format
        )
        try:
            self.usage_monitor.update_usage(char_count)
            if self.update_callback:
                self.update_callback(self.get_usage_stats())
        except Exception as e:
            self.logger.error(f"Failed to update usage: {e}")
        
        return audio_content

    def get_usage_stats(self):
        return self.usage_monitor.get_usage_stats()
    
    def get_service_name(self) -> TTSService:
        return TTSService.ELEVENLABS