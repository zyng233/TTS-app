import os
from pathlib import Path
from google.cloud import texttospeech
from google.oauth2 import service_account
from google.api_core.exceptions import GoogleAPICallError

def text_to_speech(text, output_file="output.mp3"):
    try:
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

        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Standard-C",
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        with open(output_file, "wb") as out:
            out.write(response.audio_content)
            print(f'Audio saved to {output_file}')

    except GoogleAPICallError as e:
        print(f"Google API Error: {e.message}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    text_to_speech("Hello, this is a test of Google Cloud Text-to-Speech.")