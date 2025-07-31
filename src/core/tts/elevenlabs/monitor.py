from datetime import datetime
from typing import Dict, Union, Optional
import json
import logging
import requests
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ELEVENLABS_USAGE_FILE = "elevenlabs_usage.json"
ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1/user"

class ElevenLabsUsageMonitor:
    """Tracks both local and API usage for ElevenLabs"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.usage_file = Path(ELEVENLABS_USAGE_FILE)
        self.local_char_count = 0

    def _get_current_month(self) -> str:
        """Get current month in YYYY-MM format"""
        return datetime.now().strftime("%Y-%m")

    def _load_usage_data(self) -> Dict[str, Union[str, int]]:
        """Load or initialize usage data"""
        if not self.usage_file.exists():
            return {
                'month': self._get_current_month(),
                'used': 0,
                'api_sync_time': None
            }
        
        try:
            with open(self.usage_file, 'r') as f:
                data = json.load(f)
            
            if data.get('month') != self._get_current_month():
                data = {
                    'month': self._get_current_month(),
                    'used': 0,
                    'api_sync_time': None
                }
                self._save_usage_data(data)
                
            return data
        except Exception as e:
            logger.error(f"Error loading usage data: {e}")
            return {
                'month': self._get_current_month(),
                'used': 0,
                'api_sync_time': None
            }

    def _save_usage_data(self, data: Dict) -> None:
        """Save usage data atomically"""
        try:
            temp_file = self.usage_file.with_suffix('.tmp')
            with open(temp_file, 'w') as f:
                json.dump(data, f, indent=2)
            temp_file.replace(self.usage_file)
        except Exception as e:
            logger.error(f"Failed to save usage data: {e}")

    def _get_api_usage(self) -> Optional[Dict]:
        """Fetch current usage from ElevenLabs API"""
        try:
            response = requests.get(
                ELEVENLABS_API_URL,
                headers={"xi-api-key": self.api_key}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch API usage: {e}")
            return None

    def update_usage(self, char_count: int) -> None:
        """Update local usage tracking"""
        data = self._load_usage_data()
        data['used'] = data.get('used', 0) + char_count
        self.local_char_count += char_count
        data['api_used'] = data.get('api_used', 0) + char_count
        self._save_usage_data(data)

    def get_usage_stats(self) -> Dict[str, Union[int, str]]:
        """Get combined local + API usage stats"""
        data = self._load_usage_data()
        api_data = self._get_api_usage()
        
        stats = {
            'month': data.get('month', self._get_current_month()),
            'used': data.get('used', 0),
            'source': 'local',
            'last_sync': data.get('api_sync_time')
        }
        if api_data:
            subscription = api_data.get('subscription', {})
            stats.update({
                'api_used': subscription.get('character_count', 0),
                'api_limit': subscription.get('character_limit', 0),
                'source': 'api',
                'last_sync': datetime.now().isoformat()
            })
            data['api_sync_time'] = stats['last_sync']
            self._save_usage_data(data)
        return stats

    def print_usage_report(self) -> None:
        """Print formatted usage summary"""
        stats = self.get_usage_stats()
        
        print(f"\n📊 ElevenLabs Usage for {stats['month']}")
        print(f"• Source: {stats['source'].upper()} data")
        
        if 'api_used' in stats:
            remaining = max(0, stats['api_limit'] - stats['api_used'])
            print(f"• API Usage: {stats['api_used']:,}/{stats['api_limit']:,}")
            print(f"• API Remaining: {remaining:,}")
        
        print(f"• Local Usage: {stats['used']:,} chars")
        
        if stats['last_sync']:
            print(f"• Last Synced: {stats['last_sync']}")
        else:
            print("⚠️ No recent API sync")