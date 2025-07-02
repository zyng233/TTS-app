from google.cloud import texttospeech
from google.oauth2 import service_account
from pathlib import Path

# Test standard and neural voice
def test_voices():
    creds_path = Path(__file__).parent.parent / "credentials" / "tts-key.json"
        
    if not creds_path.exists():
        raise FileNotFoundError(
            f"Google Cloud credentials not found at {creds_path}\n"
        )

    credentials = service_account.Credentials.from_service_account_file(
        str(creds_path),
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    client = texttospeech.TextToSpeechClient(credentials=credentials)
    
    # Standard voice
    standard_voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name="en-US-Standard-C" 
    )
    
    # Neural voice
    neural_voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name="en-US-Neural2-J"
    )
    
    for voice_type, voice in [("Standard", standard_voice), ("Neural", neural_voice)]:
        synthesis_input = texttospeech.SynthesisInput(text="Hello, this is a test.")
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
        
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        
        with open(f"{voice_type}_output.mp3", "wb") as out:
            out.write(response.audio_content)
        print(f"Saved {voice_type} voice sample")

# Test Speech Synthesis Markup Language (SSML)
def test_ssml():
    creds_path = Path(__file__).parent.parent / "credentials" / "tts-key.json"
        
    if not creds_path.exists():
        raise FileNotFoundError(
            f"Google Cloud credentials not found at {creds_path}\n"
        )

    credentials = service_account.Credentials.from_service_account_file(
        str(creds_path),
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    client = texttospeech.TextToSpeechClient(credentials=credentials)
    
    ssml = """
    <speak>
        Normal speech <break time="0.5s"/> 
        <prosody rate="slow">Slow speech</prosody>
        <prosody pitch="+5st">High pitch</prosody>
    </speak>
    """
    
    response = client.synthesize_speech(
        input=texttospeech.SynthesisInput(ssml=ssml),
        voice=texttospeech.VoiceSelectionParams(language_code="en-US"),
        audio_config=texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
    )
    
    with open("ssml_output.mp3", "wb") as out:
        out.write(response.audio_content)
    print("Saved SSML sample")

# Optimize audio profile for headphone and handset
def test_audio_profiles():
    creds_path = Path(__file__).parent.parent / "credentials" / "tts-key.json"
        
    if not creds_path.exists():
        raise FileNotFoundError(
            f"Google Cloud credentials not found at {creds_path}\n"
        )

    credentials = service_account.Credentials.from_service_account_file(
        str(creds_path),
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    client = texttospeech.TextToSpeechClient(credentials=credentials)
    
    for profile in ["headphone-class-device", "handset-class-device"]:
        response = client.synthesize_speech(
            input=texttospeech.SynthesisInput(text="Optimized for your device"),
            voice=texttospeech.VoiceSelectionParams(language_code="en-US"),
            audio_config=texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                effects_profile_id=[profile]  
            )
        )
        
        with open(f"{profile}_output.mp3", "wb") as out:
            out.write(response.audio_content)
        print(f"Saved {profile} sample")

# Custom voice speed/pitch
def test_custom_audio():
    creds_path = Path(__file__).parent.parent / "credentials" / "tts-key.json"
        
    if not creds_path.exists():
        raise FileNotFoundError(
            f"Google Cloud credentials not found at {creds_path}\n"
        )

    credentials = service_account.Credentials.from_service_account_file(
        str(creds_path),
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    client = texttospeech.TextToSpeechClient(credentials=credentials)
    
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=1.5,  # 50% faster
        pitch=2.0,        
        volume_gain_db=6.0
    )
    
    response = client.synthesize_speech(
        input=texttospeech.SynthesisInput(text="Custom speed and pitch"),
        voice=texttospeech.VoiceSelectionParams(language_code="en-US"),
        audio_config=audio_config
    )
    
    with open("custom_audio.mp3", "wb") as out:
        out.write(response.audio_content)
    print("Saved custom audio sample")

def list_voices():
    creds_path = Path(__file__).parent.parent / "credentials" / "tts-key.json"
        
    if not creds_path.exists():
        raise FileNotFoundError(
            f"Google Cloud credentials not found at {creds_path}\n"
        )

    credentials = service_account.Credentials.from_service_account_file(
        str(creds_path),
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    client = texttospeech.TextToSpeechClient(credentials=credentials)
    
    voices = client.list_voices()
    
    print("Available Voices:")
    for voice in voices.voices:
        print(f"{voice.name}: {voice.language_codes[0]} ({voice.ssml_gender.name})")

# test_voices()
# test_ssml()
# test_audio_profiles()
# test_custom_audio()
# list_voices()


