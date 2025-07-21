from enum import Enum
from core.tts.google_cloud import GoogleCloudTTS

class TTSService(Enum):
    GOOGLE = "google"

class TTSFactory:
    @staticmethod
    def create(service_type: TTSService = TTSService.GOOGLE, **kwargs):
        if service_type == TTSService.GOOGLE:
            return GoogleCloudTTS(**kwargs)

        raise ValueError(f"Unsupported TTS service: {service_type}")