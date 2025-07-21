from core.tts.factory import TTSFactory, TTSService

class ServiceManager:
    def __init__(self):
        self.current_service = None
        self.available_services = {
            "google": TTSService.GOOGLE,
        }
    
    def switch_service(self, service_name: str, **kwargs):
        if service_name not in self.available_services:
            raise ValueError(f"Unknown service: {service_name}")
        self.current_service = TTSFactory.create(
            self.available_services[service_name],
            **kwargs
        )
        return self.current_service