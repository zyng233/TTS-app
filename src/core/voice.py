from google.api_core.exceptions import GoogleAPICallError
from langcodes import Language
from typing import Optional, Dict, List, Union, Tuple

def get_available_languages(client, format: str = "both") -> List[Union[str, Tuple[str, str]]]:
    """Get available languages in different formats"""
    if client is None:
        raise RuntimeError("TTS client is not initialized")
    
    try:
        response = client.list_voices()
        languages = set()
        for voice in response.voices:
            lang_code = voice.language_codes[0].split('-')[0]
            languages.add((lang_code, get_language_name(lang_code)))
        
        sorted_langs = sorted(languages, key=lambda x: x[1])
        
        if format == "name":
            return [name for (code, name) in sorted_langs]
        elif format == "code":
            return [code for (code, name) in sorted_langs]
        elif format == "full":
            return [f"{name} ({code})" for (code, name) in sorted_langs]
        else:
            return sorted_langs
            
    except GoogleAPICallError as e:
        client.logger.error(f"Failed to list languages: {e.message}")
        raise RuntimeError(f"Couldn't retrieve languages: {e.message}")

def get_voices_for_language(client, language_code: str, voice_type: Optional[str] = None) -> List[Dict]:
    """Return available voices for a specific language"""
    if client is None:
        raise RuntimeError("TTS client is not initialized")
    
    try:
        response = client.list_voices(language_code=language_code)
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
        client.logger.error(f"Failed to list voices: {e.message}")
        raise RuntimeError(f"Couldn't retrieve voices: {e.message}")

def get_language_codes(client):
    """Return list of available language codes"""
    if client is None:
        raise RuntimeError("TTS client is not initialized")
    
    try:
        response = client.list_voices()
        return sorted({voice.language_codes[0].split('-')[0] 
                    for voice in response.voices})
    except GoogleAPICallError as e:
        client.logger.error(f"Failed to list language codes: {e.message}")
        raise RuntimeError(f"Couldn't retrieve language codes: {e.message}")

def validate_language_code(client, code: str) -> bool:
    """Check if language code is available"""
    return code in [lang[0] for lang in get_available_languages(client, "both")]

def get_language_name(lang_code: str) -> str:
    """Get language name"""
    return Language.get(lang_code).display_name()