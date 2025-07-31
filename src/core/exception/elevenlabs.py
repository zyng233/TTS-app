from typing import Optional, Dict
import requests
from .base import TTSAPIError

class ElevenLabsAPIError(TTSAPIError):
    """Custom exception for ElevenLabs API errors"""
    service_name = "ElevenLabs"
    
    def __init__(self, 
                 message: str, 
                 status_code: Optional[int] = None,
                 response: Optional[Dict] = None):
        """
        Args:
            message: Human-readable error description
            status_code: HTTP status code if available
            response: Full API response if available
        """
        self.status_code = status_code
        self.response = response
        details = f"Status: {status_code}" if status_code else None
        super().__init__(message, details)

    @classmethod
    def from_response(cls, response: requests.Response):
        """Factory method to create error from API response"""
        try:
            error_data = response.json()
            message = error_data.get('detail', response.text)
        except ValueError:
            message = response.text
            
        return cls(
            message=message,
            status_code=response.status_code,
            response=error_data if 'error_data' in locals() else None
        )