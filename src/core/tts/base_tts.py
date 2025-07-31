from abc import ABC, abstractmethod
from typing import Dict, Optional, Union, List, Tuple
from .service_types import TTSService

class BaseTTS(ABC):
    def __init__(self):
        """Base initialization that all TTS services must call"""
        pass
    
    @abstractmethod
    def generate_to_memory(self, text: str, **kwargs) -> bytes:
        """Generate audio with business logic"""
        pass
    
    @abstractmethod
    def get_usage_stats(self) -> Dict[str, Union[int, str]]:
        """Get combined usage statistics"""
        pass
    
    @abstractmethod
    def get_available_voices(self, model: Optional[str] = None, language_code: Optional[str] = None) -> List[Dict]:
        """Get available voices with error handling"""
        pass
    
    @abstractmethod
    def get_available_languages(self, format: str = "code") -> List[Union[str, Tuple[str, str]]]:
        """Get supported languages with error handling"""
        pass
    
    @abstractmethod
    def get_service_name(self) -> TTSService:
        pass