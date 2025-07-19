from google.cloud import monitoring_v3, billing_v1
from datetime import datetime
from collections import defaultdict
from typing import Dict, Union

FREE_TIER_CHAR_LIMIT = 1000000

def get_billing_usage(tts_generator) -> Dict[str, int]:
    """Fetch TTS usage from Billing Reports"""
    client = billing_v1.CloudBillingClient(credentials=tts_generator.credentials)
    
    billing_accounts = list(client.list_billing_accounts())
    if not billing_accounts:
        raise RuntimeError("No billing accounts found")
    
    service = billing_v1.services.ServiceUsageClient(credentials=tts_generator.credentials)
    now = datetime.now()
    
    response = service.list_services(
        parent=f"projects/{tts_generator.credentials.project_id}",
        filter='state:ENABLED'
    )

    usage_by_type = defaultdict(int)
    voice_type_mapping = {
        '9D01-5995-B545': 'Standard',
        'FEBD-04B6-769B': 'WaveNet',
        'F977-2280-6F1B': 'Chirp',
        '84AB-48C0-F9C3': 'Studio'
    }
    
    for item in response:
        sku = item.name.split('/')[-1]
        if sku in voice_type_mapping:
            voice_type = voice_type_mapping[sku]
            usage_by_type[voice_type] += int(item.usage.amount)
    
    return dict(usage_by_type)
    
def get_character_usage(client) -> Dict[str, Union[int, str]]:
    """Get character usage from the most reliable available source"""
    if client is None:
        raise RuntimeError("TTS client is not initialized")
    
    monitoring_used = try_monitoring_api(client.credentials)
    if monitoring_used is not None:
        return {
            'used': monitoring_used,
            'source': 'monitoring'
        }
    
    try:
        detailed_usage = get_billing_usage(client)
        total_used = sum(detailed_usage.values())
        return {
            'used': total_used,
            'source': 'billing',
            'detailed_usage': detailed_usage
        }
    except Exception as e:
        print(f"[DEBUG] Billing API attempt failed: {e}")
        return {
            'used': 0,
            'source': 'fallback'
        }

def try_monitoring_api(credentials) -> Union[int, None]:
    """Attempt to get usage from Monitoring API"""
    try:
        client = monitoring_v3.MetricServiceClient(credentials=credentials)
        project_name = f"projects/{credentials.project_id}"
        print(credentials.project_id)
        now = datetime.now()
        start_of_month = datetime(now.year, now.month, 1)
        
        interval = monitoring_v3.TimeInterval({
            "start_time": {"seconds": int(start_of_month.timestamp())},
            "end_time": {"seconds": int(now.timestamp())}
        })
        
        response = list(client.list_time_series(
            name=project_name,
            filter=(
                'metric.type="serviceruntime.googleapis.com/quota/allocation/usage" AND '
                'metric.labels.quota_metric="speech.googleapis.com/default_num_characters" AND '
                'resource.labels.service="speech.googleapis.com"'
            ),
            interval=interval,
            view=monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL
        ))
        
        if response and response[0].points:
            return int(response[0].points[-1].value.int64_value)
    except Exception as e:
        print(f"[DEBUG] Monitoring API attempt failed: {e}")
    return None

def get_character_stats(client):
    """Get current character usage stats"""
    if client is None:
        raise RuntimeError("TTS client is not initialized")
    
    usage_data = get_character_usage(client)
    
    result = {
        'used': usage_data['used'],
        'remaining': max(0, FREE_TIER_CHAR_LIMIT - usage_data['used']),
        'limit': FREE_TIER_CHAR_LIMIT,
        'month': datetime.now().strftime("%Y-%m"),
        'source': usage_data['source']
    }
    
    if 'detailed_usage' in usage_data:
        result['detailed_usage'] = usage_data['detailed_usage']
    
    return result
       
def print_character_usage(client=None) -> None:
    """Print current character usage information"""
    stats = get_character_stats(client)
    
    source_map = {
        'monitoring': 'Google Cloud Monitoring',
        'billing': 'Google Billing Reports',
        'fallback': 'Fallback estimate'
    }
    
    print(f"\n📊 Character Usage for {stats['month']}")
    print(f"• Source: {source_map.get(stats['source'], stats['source'])}")
    print(f"• Used: {stats['used']:,}/{stats['limit']:,} characters")
    print(f"• Remaining: {stats['remaining']:,} characters")
    
    if 'detailed_usage' in stats:
        print("\n🔍 Detailed Usage by Voice Type:")
        for voice_type, count in stats['detailed_usage'].items():
            print(f"  - {voice_type} voices: {count:,} characters")