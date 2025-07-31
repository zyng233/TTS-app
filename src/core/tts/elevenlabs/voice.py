import requests
from typing import Dict, List, Optional, Union, Tuple
from core.tts.base_voice import BaseVoiceManager, BaseVoiceDetails
from ...exception.elevenlabs import ElevenLabsAPIError
from langcodes import Language

class ElevenLabsVoiceDetails(BaseVoiceDetails):
    """ElevenLabs-specific voice details formatting"""
    
    @staticmethod
    def format_details(voice_data: Dict) -> str:
        parts = []
        gender = voice_data.get("gender") or voice_data.get("labels", {}).get("gender")
        if gender:
            parts.append(f"Gender: {gender.capitalize()}")

        accent = voice_data.get("accent") or voice_data.get("labels", {}).get("accent")
        if accent:
            parts.append(f"Accent: {accent.capitalize()}")

        age = voice_data.get("labels", {}).get("age")
        if age:
            parts.append(f"Age: {age}")

        locale = voice_data.get("locale")
        if locale:
            parts.append(f"Locale: {locale}")

        voice_type = voice_data.get("type")
        if voice_type:
            parts.append(f"Type: {voice_type.capitalize()}")

        if desc := voice_data.get("description"):
            parts.append(f"Desc: {desc[:40]}...")

        return " | ".join(parts) if parts else "No voice details available"
    
class ElevenLabsVoiceManager(BaseVoiceManager):
    """Handles all voice and language operations for ElevenLabs"""
    
    BASE_URL = "https://api.elevenlabs.io/v1"
    
    def __init__(self, api_key: str):
        super().__init__() 
        self.api_key = api_key
        self._voices_cache = None
        self._language_cache = {}


    def _fetch_voices(self) -> List[Dict]:
        """Fetch and cache voices from API"""
        try:
            response = requests.get(
                f"{self.BASE_URL}/voices",
                headers={"xi-api-key": self.api_key}
            )
            response.raise_for_status()
            return response.json().get("voices", [])
        except requests.exceptions.RequestException as e:
            raise ElevenLabsAPIError(f"Voice fetch failed: {str(e)}")

    def get_available_languages(self, model: Optional[str] = None, format: str = "both") -> List[Union[str, Tuple[str, str]]]:
        """
        Get available languages in different formats
        Args:
            model: internal model ID like 'eleven_multilingual_v2'
            format: 'name', 'full', or 'both' (returns tuples of name only)
        """
        cache_key = model or "ALL"
        if cache_key in self._language_cache:
            sorted_langs = self._language_cache[cache_key]
        else:
            voices = self._fetch_voices()
            languages = set()
            
            for voice in voices:
                verified = voice.get("verified_languages", [])
                for lang_entry in verified:
                    voice_model = lang_entry.get("model_id")
                    if model and voice_model != model:
                        continue

                    raw_lang = lang_entry.get("language")
                    if not raw_lang:
                        continue

                    lang_code = raw_lang.split("-")[0]
                    try:
                        lang_name = self.get_language_name(lang_code)
                    except Exception:
                        continue
                    
                    languages.add((lang_code, lang_name))
                    
            sorted_langs = sorted(languages, key=lambda x: x[1])
            self._language_cache[cache_key] = sorted_langs
            
        if format == "name":
            return [name for (_, name) in sorted_langs]
        elif format == "code":
            return [code for (code, _) in sorted_langs]
        elif format == "full":
            return [f"{name} ({code})" for (code, name) in sorted_langs]
        return sorted_langs

    def get_voices_for_language(self, language_code: str, voice_type: Optional[str] = None) -> List[Dict]:
        """
        Get voices filtered by language code (e.g., 'en', 'zh', 'es').

        Args:
            language_code: ISO language code (e.g., 'en' for English, 'zh' for Chinese)
            voice_type: 'premade' or 'cloned' (None for all)
        """
        voices = self._fetch_voices()
        filtered = []
        target_code = language_code.lower()

        for voice in voices:
            verified_languages = voice.get("verified_languages", [])
            for lang_entry in verified_languages:
                lang_code = lang_entry.get("language", "").split("-")[0].lower()
                if lang_code == target_code:
                    voice_data = {
                        'id': voice['voice_id'],
                        'name': voice['name'],
                        'gender': voice.get('labels', {}).get('gender', 'unknown'),
                        'language': lang_code,
                        'accent': lang_entry.get("accent", 'standard'),
                        'locale': lang_entry.get("locale", None),
                        'type': 'premade' if voice.get('category') == 'premade' else 'cloned',
                        'settings': voice.get('settings', {}),
                        'preview_url': lang_entry.get("preview_url", voice.get("preview_url"))
                    }
                    if voice_type is None or voice_data['type'] == voice_type:
                        filtered.append(voice_data)
                    break
        return filtered
    
    def get_language_name(self, lang_code: str) -> str:
        """Return a human-readable language name from a code."""
        return Language.get(lang_code).display_name()
    
    @staticmethod
    def format_voice_details(voice_data: Dict) -> str:
        return ElevenLabsVoiceDetails.format_details(voice_data)