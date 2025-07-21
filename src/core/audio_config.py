from google.cloud import texttospeech
from google.api_core.exceptions import GoogleAPICallError
from typing import Optional, Dict
from .voice import get_language_codes, get_voices_for_language

AUDIO_FORMATS = {
    "MP3": texttospeech.AudioEncoding.MP3,
    "WAV": texttospeech.AudioEncoding.LINEAR16,
    "OGG": texttospeech.AudioEncoding.OGG_OPUS
}

def generate_to_memory(
    client,
    text: str,
    voice_name: Optional[str] = None,
    voice_data: Optional[Dict] = None,
    audio_format: str = "MP3",
    speaking_rate: float = 1.0,
    pitch: float = 0.0,
    is_ssml: bool = False,
    effects_profile_id: Optional[list[str]] = None
) -> bytes:
    """
    Generate speech and return audio binary data
    
    Args:
        text: Input text/SSML
        voice_name: Voice name (e.g., "en-US-Wavenet-D")
        voice_data: Full voice parameters (overrides voice_name)
        audio_format: Output format
        speaking_rate: Speed multiplier
        pitch: Pitch adjustment
        is_ssml: Whether input is SSML
        effects_profile_id: List of audio effects profiles (e.g. ["headphone-class-device"])
    """
    voice_params = voice_data or {"name": voice_name or "en-US-Wavenet-D"}
    
    try:
        if audio_format.upper() not in AUDIO_FORMATS:
            raise ValueError(f"Unsupported audio format: {audio_format}")

        synthesis_input = (
            texttospeech.SynthesisInput(ssml=text) if is_ssml
            else texttospeech.SynthesisInput(text=text))
        
        voice = prepare_voice_params(client, voice_name, voice_params)
        
        audio_config = texttospeech.AudioConfig(
            audio_encoding=AUDIO_FORMATS[audio_format.upper()],
            speaking_rate=speaking_rate,
            pitch=pitch,
            effects_profile_id=effects_profile_id or []
        )

        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        return response.audio_content

    except GoogleAPICallError as e:
        raise RuntimeError(f"Google TTS API error: {e.message}") from e
    except Exception as e:
        raise RuntimeError(f"Speech generation failed: {str(e)}") from e

def prepare_voice_params(client, voice_name: str, custom_params: Optional[Dict] = None):
    """Prepare voice parameters from presets or custom values."""
    if custom_params:
        return texttospeech.VoiceSelectionParams(**custom_params)
    
    for lang_code in get_language_codes(client):
        voices = get_voices_for_language(client, lang_code)
        for voice in voices:
            if voice['name'] == voice_name:
                return texttospeech.VoiceSelectionParams(
                    language_code=voice['language'],
                    name=voice['name'],
                    ssml_gender=getattr(texttospeech.SsmlVoiceGender, voice['gender'])
                )
                
    parts = voice_name.split("-")
    if len(parts) >= 3:
        language_code = "-".join(parts[:2])
        return texttospeech.VoiceSelectionParams(
            language_code=language_code,
            name=voice_name,
            ssml_gender=texttospeech.SsmlVoiceGender.MALE
        )    
        
    return texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name="en-US-Wavenet-D",
        ssml_gender=texttospeech.SsmlVoiceGender.MALE
    )