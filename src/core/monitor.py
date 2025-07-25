from datetime import datetime
from typing import Dict, Union
import json
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FREE_TIER_CHAR_LIMIT = 1000000
USAGE_FILE = "tts_usage.json"

def safe_get_month() -> str:
    """Always return current month in correct format"""
    return datetime.now().strftime("%Y-%m")

def load_or_create_data() -> Dict[str, Union[str, int]]:
    """Atomic load or create of usage data"""
    current_month = safe_get_month()
    default_data = {'month': current_month, 'used': 0}
    
    if not os.path.exists(USAGE_FILE):
        try:
            with open(USAGE_FILE, 'w') as f:
                json.dump(default_data, f)
            return default_data
        except Exception as e:
            logger.error(f"Failed to create usage file: {e}")
            return default_data
    
    try:
        with open(USAGE_FILE, 'r') as f:
            data = json.load(f)
            
        if not isinstance(data, dict):
            raise ValueError("Data is not a dictionary")
        if 'month' not in data or 'used' not in data:
            raise ValueError("Missing required fields")
        
        if data['month'] != current_month:
            data = default_data
            with open(USAGE_FILE, 'w') as f:
                json.dump(data, f)
                
        return data
    except Exception as e:
        logger.error(f"Error loading usage data: {e}")
        return default_data

def update_usage(char_count: int):
    """Thread-safe usage update"""
    try:
        current_month = safe_get_month()
        with open(USAGE_FILE, 'r+') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {'month': current_month, 'used': 0}
                logger.warning("Created new usage file - invalid JSON")
            except FileNotFoundError:
                data = {'month': current_month, 'used': 0}
                logger.warning("Created new usage file - didn't exist")
                
            if data.get('month') != current_month:
                data = {'month': current_month, 'used': 0}
                logger.info("Month changed - reset usage counter")
                
            data['used'] = data.get('used', 0) + char_count
            f.seek(0)
            json.dump(data, f, indent=2)
            f.truncate()
            logger.debug(f"Updated usage: {data}")
    except Exception as e:
        logger.error(f"Failed to update usage: {e}")

def get_character_stats(client=None):
    """Completely safe stats retrieval"""
    try:
        data = load_or_create_data()
        used = data.get('used', 0)
        current_month = safe_get_month()

        return {
            'used': used,
            'remaining': max(0, FREE_TIER_CHAR_LIMIT - used),
            'limit': FREE_TIER_CHAR_LIMIT,
            'month': current_month,
            'source': 'local',
            'warning': '' if data.get('month') == current_month else 'Month reset detected'
        }
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return {
            'used': 0,
            'remaining': FREE_TIER_CHAR_LIMIT,
            'limit': FREE_TIER_CHAR_LIMIT,
            'month': safe_get_month(),
            'source': 'error',
            'warning': str(e)
        }

def print_character_usage(client=None) -> None:
    """Print current character usage information"""
    stats = get_character_stats(client)
    
    print(f"\n📊 Character Usage for {stats['month']}")
    print(f"• Source: {stats['source']}")
    print(f"• Used: {stats['used']:,}/{stats['limit']:,} characters")
    print(f"• Remaining: {stats['remaining']:,} characters")
    
    if stats.get('warning'):
        print(f"\n⚠️ Note: {stats['warning']}")