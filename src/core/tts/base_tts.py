from abc import ABC, abstractmethod
from typing import Dict, Optional, Union

class BaseTTS(ABC):
    @abstractmethod
    def generate_to_memory(self, text: str, **kwargs) -> bytes:
        """Generate audio from text and return as bytes"""
        pass
    
    @abstractmethod
    def get_usage_stats(self) -> Dict[str, Union[int, str]]:
        """Get current usage statistics"""
        pass
    
    @abstractmethod
    def get_available_voices(self, language_code: Optional[str] = None) -> list:
        """List available voices for language"""
        pass
    
    @abstractmethod
    def get_available_languages(self) -> list:
        """List supported languages"""
        pass