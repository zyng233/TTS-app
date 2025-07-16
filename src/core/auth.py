from pathlib import Path
from google.oauth2 import service_account
from google.cloud import texttospeech
import sys

def get_credentials_path() -> Path:
    """Path resolution"""
    base_path = Path(getattr(sys, '_MEIPASS', Path(__file__).parent.parent))
    
    possible_paths = [
        # 1. Explicitly specified path (handled in __init__)
        # 2. Next to executable (for release version)
        Path(sys.executable).parent / "credentials" / "credentials.json",
        
        # 3. In bundled app resources (PyInstaller)
        base_path / "credentials" / "credentials.json",
        
        # 4. User config directory (cross-platform)
        Path.home() / ".tts_app" / "credentials.json",
        
        # 5. Development repo location
        Path(__file__).parent.parent.parent / "credentials" / "credentials.json"
    ]

    for path in possible_paths:
        if path.exists():
            return path

    default_path = Path(sys.executable).parent / "credentials" / "credentials.json"
    default_path.parent.mkdir(exist_ok=True, parents=True)
    return default_path

def validate_credentials(credentials_path: Path) -> None:
    if not credentials_path.exists():
        raise FileNotFoundError(
            f"Google Cloud credentials not found at {credentials_path}\n"
        )

def initialize_client(credentials_path: Path):
    try:
        credentials = service_account.Credentials.from_service_account_file(
            str(credentials_path),
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        client = texttospeech.TextToSpeechClient(credentials=credentials)
        return client, credentials
    except Exception as e:
        print(f"Client creation failed: {str(e)}")
        raise