from typing import Dict, List, Tuple, Union, Optional
from abc import ABC, abstractmethod
from langcodes import Language

class BaseVoiceDetails(ABC):
    """Abstract base class for voice details formatting"""
    
    @staticmethod
    @abstractmethod
    def format_details(voice_data: Dict) -> str:
        """Format voice details for display"""
        pass

class BaseVoiceManager(ABC):
    """Abstract base class for voice management across services"""
    
    def __init__(self):
        """Base initialization that all voice managers must call"""
        pass 
    
    @abstractmethod
    def get_available_languages(self, format: str = "both") -> List[Union[str, Tuple[str, str]]]:
        """Get available languages in different formats"""
        pass
    
    @abstractmethod
    def get_voices_for_language(self, language_code: str, voice_type: Optional[str] = None) -> List[Dict]:
        """Get voices filtered by language"""
        pass
    
    @staticmethod
    def format_voice_details(voice_data: Dict) -> str:
        """Default voice details formatting"""
        return BaseVoiceDetails.format_details(voice_data)