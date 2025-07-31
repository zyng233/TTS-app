from core.tts.google.voice import GoogleVoiceManager
from core.tts.elevenlabs.voice import ElevenLabsVoiceManager
from core.tts.base_voice import BaseVoiceManager
from typing import Union

class VoiceManagerFactory:
    """Creates appropriate voice manager for TTS services"""
    
    @staticmethod
    def create(service_type: str, config: Union[dict, object]) -> BaseVoiceManager:
        """
        Create voice manager for specified service
        Args:
            service_type: 'google' or 'elevenlabs'
            config: For Google - client object, for ElevenLabs - {'api_key': str}
        """
        if service_type == 'google':
            return GoogleVoiceManager(client=config)
        elif service_type == 'elevenlabs':
            if not isinstance(config, dict) or 'api_key' not in config:
                raise ValueError("ElevenLabs config must be a dict with 'api_key'")
            return ElevenLabsVoiceManager(api_key=config['api_key'])
        else:
            raise ValueError(f"Unsupported service type: {service_type}")