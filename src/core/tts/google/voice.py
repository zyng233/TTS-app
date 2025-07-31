from google.api_core.exceptions import GoogleAPICallError
from langcodes import Language
from typing import Optional, Dict, List, Union, Tuple
from core.tts.base_voice import BaseVoiceManager, BaseVoiceDetails

class GoogleVoiceDetails(BaseVoiceDetails):
    """Google-specific voice details formatting"""
    
    @staticmethod
    def format_details(voice_data: Dict) -> str:
        details = []
        if 'gender' in voice_data:
            details.append(f"Gender: {voice_data['gender']}")
        if 'voice_type' in voice_data:
            details.append(f"Engine: {voice_data['voice_type']}")
        if 'sample_rate' in voice_data:
            details.append(f"{voice_data['sample_rate']//1000}kHz")
        return " | ".join(details)
    
class GoogleVoiceManager(BaseVoiceManager):
    """Handles Google Cloud TTS voice operations"""
    
    def __init__(self, client):
        super().__init__()
        self.client = client
        
    def get_available_languages(self, model: Optional[str] = None, format: str = "both") -> List[Union[str, Tuple[str, str]]]:
        try:
            response = self.client.list_voices()
            languages = set()
            for voice in response.voices:
                lang_code = voice.language_codes[0].split('-')[0]
                languages.add((lang_code, self.get_language_name(lang_code)))
            
            sorted_langs = sorted(languages, key=lambda x: x[1])
            
            if format == "name":
                return [name for (_, name) in sorted_langs]
            elif format == "code":
                return [code for (code, _) in sorted_langs]
            elif format == "full":
                return [f"{name} ({code})" for (code, name) in sorted_langs]
            return sorted_langs
                
        except GoogleAPICallError as e:
            raise RuntimeError(f"Couldn't retrieve languages: {e.message}")
    
    def get_voices_for_language(self, language_code: str, voice_type: Optional[str] = None) -> List[Dict]:
        try:
            response = self.client.list_voices(language_code=language_code)
            voices = [{
                'name': voice.name,
                'gender': voice.ssml_gender.name,
                'language': voice.language_codes[0],
                'sample_rate': voice.natural_sample_rate_hertz,
                'voice_type': 'Neural' if 'Neural' in voice.name else 'WaveNet'
            } for voice in response.voices]
            
            if voice_type:
                return [v for v in voices if v['voice_type'] == voice_type]
            return voices
            
        except GoogleAPICallError as e:
            raise RuntimeError(f"Couldn't retrieve voices: {e.message}")
    
    def get_language_codes(self) -> List[str]:
        try:
            response = self.client.list_voices()
            return sorted({voice.language_codes[0].split('-')[0] 
                        for voice in response.voices})
        except GoogleAPICallError as e:
            raise RuntimeError(f"Couldn't retrieve language codes: {e.message}")
    
    def validate_language_code(self, code: str) -> bool:
        return code in [lang[0] for lang in self.get_available_languages("both")]
    
    def get_language_name(self, lang_code: str) -> str:
        """Get language name"""
        return Language.get(lang_code).display_name()
    
    @staticmethod
    def format_voice_details(voice_data: Dict) -> str:
        return GoogleVoiceDetails.format_details(voice_data)