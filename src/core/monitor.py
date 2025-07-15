from google.cloud import monitoring_v3
from datetime import datetime

FREE_TIER_LIMITS = {
    'characters': 1000000,
    'requests': 1000
}

def get_real_time_quota(client):
    """Fetch actual usage from Google Cloud Monitoring"""
    monitor_client = monitoring_v3.MetricServiceClient(credentials=client._credentials)
    project_id = client._credentials.project_id
    project_name = f"projects/{project_id}"
    
    characters_metric = (
        "serviceruntime.googleapis.com/quota/allocation/usage"
        "?metric.labels.quota_metric=speech.googleapis.com%2Fdefault_requests"
        "&resource.labels.service=speech.googleapis.com"
    )
    
    requests_metric = (
        "serviceruntime.googleapis.com/quota/allocation/usage"
        "?metric.labels.quota_metric=speech.googleapis.com%2Fcharacters"
        "&resource.labels.service=speech.googleapis.com"
    )
    
    try:
        # Get characters usage
        characters_response = monitor_client.list_time_series(
            name=project_name,
            filter_=characters_metric,
            interval=monitoring_v3.TimeInterval(),
            view=monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL
        )
        
        # Get requests usage
        requests_response = monitor_client.list_time_series(
            name=project_name,
            filter_=requests_metric,
            interval=monitoring_v3.TimeInterval(),
            view=monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL
        )
        
        return {
            "characters_used": extract_metric_value(characters_response),
            "requests_used": extract_metric_value(requests_response),
        }
        
    except Exception as e:
        return {"characters_used": 0, "requests_used": 0}

def extract_metric_value(response) -> int:
    """Extract numeric value from monitoring API response"""
    for series in response:
        for point in series.points:
            return int(point.value.int64_value)
    return 0

def get_usage_stats(client):
    """Get usage stats"""
    try:
        cloud_data = get_real_time_quota()
        return {
            'characters_used': cloud_data['characters_used'],
            'characters_remaining': max(0, FREE_TIER_LIMITS['characters'] - cloud_data['characters_used']),
            'requests_used': cloud_data['requests_used'],
            'requests_remaining': max(0, FREE_TIER_LIMITS['requests'] - cloud_data['requests_used']),
            'month': datetime.now().strftime("%Y-%m"),
            'source': 'google_cloud' 
        }
    except Exception as e:
        return {
            'characters_used': client.usage_data['characters_used'],
            'characters_remaining': max(0, FREE_TIER_LIMITS['characters'] - client.usage_data['characters_used']),
            'requests_used': client.usage_data['requests_used'],
            'requests_remaining': max(0, FREE_TIER_LIMITS['requests'] - client.usage_data['requests_used']),
            'month': client.usage_data['month'],
            'source': 'local_cache' 
        }
        
def print_usage() -> None:
    stats = get_usage_stats()
    source_note = "(Google Cloud data)" if stats['source'] == 'google_cloud' else "(local estimate)"
        
    print(f"\n📊 Usage for {stats['month']} {source_note}:")
    print(f"• Characters: {stats['characters_used']:,}/{FREE_TIER_LIMITS['characters']:,}")
    print(f"• Requests: {stats['requests_used']:,}/{FREE_TIER_LIMITS['requests']:,}")