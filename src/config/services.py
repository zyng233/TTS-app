from dataclasses import dataclass
from enum import Enum
from pathlib import Path

@dataclass
class ServiceConfig:
    active_service: str = "google"
    google_credentials: Path = Path("credentials/google.json")