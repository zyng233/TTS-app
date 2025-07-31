from enum import Enum
from .tts.factory import TTSService, TTSFactory

class ServiceManager:
    def __init__(self):
        self.current_service = None
        self.available_services = {
            "google": TTSService.GOOGLE,
            "elevenlabs": TTSService.ELEVENLABS
        }
    
    def switch_service(self, service_name: str, **kwargs):
        if service_name not in self.available_services:
            raise ValueError(f"Unknown service: {service_name}")
        
        service_enum = self.available_services[service_name]
        self.current_service = TTSFactory.create(service_enum, **kwargs)
        return self.current_service