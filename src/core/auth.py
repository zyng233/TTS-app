from pathlib import Path
import sys
from typing import Tuple, Any
import json
from core.tts.service_types import TTSService

class AuthManager:
    def __init__(self):
        self.service_configs = {
            TTSService.GOOGLE: { 
                'config_name': 'google.json',
                'validator': lambda path: self._validate_creds(TTSService.GOOGLE, path),
                'initializer': self._init_google_client
            },
            
            TTSService.ELEVENLABS: {
                'config_name': 'elevenlabs.json',
                'validator': lambda path: self._validate_creds(TTSService.ELEVENLABS, path),
                'initializer': self._init_elevenlabs_client
            }
        }

    def get_credentials_path(self, service: TTSService) -> Path:
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

    def validate_credentials(self, service: TTSService, credentials_path: Path) -> None:
        """Validate credentials for specified service"""
        if service not in self.service_configs:
            raise ValueError(f"Unsupported service: {service}")
        
        validator = self.service_configs[service]['validator']
        validator(credentials_path)

    def initialize_client(self, service: TTSService, credentials_path: Path) -> Tuple[Any, Any]:
        """Initialize client for specified service"""
        if service not in self.service_configs:
            raise ValueError(f"Unsupported service: {service}")
        
        initializer = self.service_configs[service]['initializer']
        return initializer(credentials_path)

    def _validate_creds(self, service: TTSService, credentials_path: Path) -> None:
        """Common credential validation for all services"""
        if not credentials_path.exists():
            raise FileNotFoundError(
                f"{service.value.capitalize()} credentials not found at {credentials_path}\n"
                f"Please create a JSON file with your {service.value} credentials"
            )
        
        try:
            with open(credentials_path) as f:
                creds = json.load(f)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid {service.value} credentials JSON file")
    
    # Google Cloud methods
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
        
    # ElevenLabs methods
    def _init_elevenlabs_client(self, credentials_path: Path) -> Tuple[Any, Any]:
        """Simplified ElevenLabs initialization"""
        try:
            with open(credentials_path) as f:
                creds = json.load(f)
                from .tts.elevenlabs.elevenlabs import ElevenLabsTTS
                return ElevenLabsTTS(creds['api_key']), None
        except Exception as e:
            raise RuntimeError(f"ElevenLabs initialization failed: {str(e)}")
        
    def get_api_key(self, service: TTSService) -> str:
        """Get API key for specified service"""
        if service not in self.service_configs:
            raise ValueError(f"Unsupported service: {service}")
            
        credentials_path = self.get_credentials_path(service)
        self.validate_credentials(service, credentials_path)
        
        with open(credentials_path) as f:
            creds = json.load(f)
            
        if service == TTSService.ELEVENLABS:
            return creds.get('api_key')
        elif service == TTSService.GOOGLE:
            return None
        else:
            raise ValueError(f"API key retrieval not implemented for {service}")