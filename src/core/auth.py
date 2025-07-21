from pathlib import Path
from enum import Enum
import sys
from typing import Tuple, Any
import json

class ServiceType(Enum):
    GOOGLE = "google"

class AuthManager:
    def __init__(self):
        self.service_configs = {
            ServiceType.GOOGLE: {
                'config_name': 'google.json',
                'validator': self._validate_google_creds,
                'initializer': self._init_google_client
            }
        }

    def get_credentials_path(self, service: ServiceType) -> Path:
        """Get path for service credentials file"""
        base_path = Path(getattr(sys, '_MEIPASS', Path(__file__).parent.parent))
        possible_paths = [
            Path(sys.executable).parent / "credentials" / self.service_configs[service]['config_name'],
            base_path / "credentials" / self.service_configs[service]['config_name'],
            Path.home() / ".tts_app" / self.service_configs[service]['config_name'],
            Path(__file__).parent.parent.parent / "credentials" / self.service_configs[service]['config_name']
        ]

        for path in possible_paths:
            if path.exists():
                return path

        default_path = Path(sys.executable).parent / "credentials" / self.service_configs[service]['config_name']
        default_path.parent.mkdir(exist_ok=True, parents=True)
        return default_path

    def validate_credentials(self, service: ServiceType, credentials_path: Path) -> None:
        """Validate credentials for specified service"""
        validator = self.service_configs[service]['validator']
        validator(credentials_path)

    def initialize_client(self, service: ServiceType, credentials_path: Path) -> Tuple[Any, Any]:
        """Initialize client for specified service"""
        initializer = self.service_configs[service]['initializer']
        return initializer(credentials_path)

    def _validate_google_creds(self, credentials_path: Path) -> None:
        if not credentials_path.exists():
            raise FileNotFoundError(
                f"Google Cloud credentials not found at {credentials_path}\n"
                "Please download credentials JSON file from Google Cloud Console"
            )
        
        try:
            with open(credentials_path) as f:
                json.load(f)  # Validate JSON format
        except json.JSONDecodeError:
            raise ValueError("Invalid Google credentials JSON file")

    def _init_google_client(self, credentials_path: Path) -> Tuple[Any, Any]:
        from google.oauth2 import service_account
        from google.cloud import texttospeech
        
        try:
            credentials = service_account.Credentials.from_service_account_file(
                str(credentials_path),
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
            client = texttospeech.TextToSpeechClient(credentials=credentials)
            return client, credentials
        except Exception as e:
            raise RuntimeError(f"Google client initialization failed: {str(e)}")