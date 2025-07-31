from typing import Type
from .base_tts import BaseTTS
from .google.google_cloud import GoogleCloudTTS
from .elevenlabs.elevenlabs import ElevenLabsTTS
from .service_types import TTSService

class TTSFactory:
    SERVICE_MAPPING: dict[TTSService, Type[BaseTTS]] = {
        TTSService.GOOGLE: GoogleCloudTTS,
        TTSService.ELEVENLABS: ElevenLabsTTS 
    }
    
    @staticmethod
    def create(service_type: TTSService = TTSService.GOOGLE, auth_manager=None, **kwargs) -> BaseTTS:
        tts_class = TTSFactory.SERVICE_MAPPING.get(service_type)
        if not tts_class:
            raise ValueError(f"Unsupported TTS service: {service_type}")
        
        if service_type == TTSService.GOOGLE:
            return tts_class(
                credentials_path=auth_manager.get_credentials_path(service_type) if auth_manager else None,
                update_callback=kwargs.get('update_callback'),
                auth_manager=auth_manager
            )
        elif service_type == TTSService.ELEVENLABS:
            api_key = auth_manager.get_api_key(service_type) if auth_manager else None
            return tts_class(
                api_key=api_key,
                update_callback=kwargs.get('update_callback'),
                auth_manager=auth_manager
            )
        
        return tts_class(**kwargs)