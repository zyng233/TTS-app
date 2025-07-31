from typing import Optional

class TTSAPIError(Exception):
    """Base class for all TTS API errors with common formatting"""
    service_name = "Generic TTS"
    
    def __init__(self, message: str, details: Optional[str] = None):
        self.details = details
        full_message = f"{self.service_name} Error: {message}"
        if details:
            full_message += f" (Details: {details})"
        super().__init__(full_message)