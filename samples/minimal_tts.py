import sys
from pathlib import Path
from google.cloud import texttospeech
from google.oauth2 import service_account
from google.api_core.exceptions import GoogleAPICallError

class TTSGenerator:
    def __init__(self):
        self.credentials_path = Path(__file__).parent.parent.parent / "credentials" / "google.json"
        self._validate_credentials()

    def _validate_credentials(self):
        if not self.credentials_path.exists():
            raise FileNotFoundError(
                f"Google Cloud credentials not found at {self.credentials_path}\n"
            )

    def _initialize_client(self):
        credentials = service_account.Credentials.from_service_account_file(
            str(self.credentials_path),
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        return texttospeech.TextToSpeechClient(credentials=credentials)

    def generate_speech(self, text, output_file="output.mp3", is_ssml=False, voice_params=None):
        """
        Convert text/SSML to speech audio file.
        
        Args:
            text: Input text or SSML content
            output_file: Output filename
            is_ssml: Whether input is SSML markup
            voice_params: Custom voice parameters (optional)
        """
        try:
            client = self._initialize_client()

            synthesis_input = texttospeech.SynthesisInput(text=text)
            if is_ssml:
                synthesis_input = texttospeech.SynthesisInput(ssml=text)
            
            voice = voice_params or texttospeech.VoiceSelectionParams(
                language_code="en-US",
                name="en-US-Wavenet-D",
                ssml_gender=texttospeech.SsmlVoiceGender.MALE
            )

            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )

            response = client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )

            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "wb") as out:
                out.write(response.audio_content)
            
            return output_path

        except GoogleAPICallError as e:
            raise RuntimeError(f"Google TTS API error: {e.message}") from e
        except Exception as e:
            raise RuntimeError(f"Speech generation failed: {str(e)}") from e

def main():
    print("=== Google Cloud TTS Generator ===")
    
    try:
        tts = TTSGenerator()
        
        ssml_path = Path(__file__).parent.parent.parent / "samples" / "se_text.ssml"
        if not ssml_path.exists():
            raise FileNotFoundError(f"SSML file not found at: {ssml_path}")
        
        with open(ssml_path, "r", encoding="utf-8") as f:
            ssml_content = f.read()
        
        output_path = tts.generate_speech(
            text=ssml_content,
            output_file="se_concept.mp3",
            is_ssml=True
        )
        
        print(f"\n✅ Successfully generated audio at: {output_path}")
        return 0
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())