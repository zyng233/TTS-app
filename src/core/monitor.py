from google.cloud import monitoring_v3
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp

FREE_TIER_LIMITS = {
    'characters': 1000000,
    'requests': 1000
}

def get_real_time_quota(tts_generator):
    """Fetch actual usage from Google Cloud Monitoring"""
    monitor_client = monitoring_v3.MetricServiceClient(credentials=tts_generator.credentials)
    project_id = tts_generator.credentials.project_id
    project_name = f"projects/{project_id}"
    print(f"[DEBUG] Using project: {project_id}")
    
    now = datetime.now()
    start_of_month = datetime(now.year, now.month, 1)
    
    start_time_proto = Timestamp()
    start_time_proto.FromDatetime(start_of_month)

    end_time_proto = Timestamp()
    end_time_proto.FromDatetime(now)

    interval = monitoring_v3.TimeInterval(
        start_time=start_time_proto,
        end_time=end_time_proto
    )
    
    characters_metric = (
        'metric.type="serviceruntime.googleapis.com/quota/allocation/usage" AND '
        'metric.labels.quota_metric="speech.googleapis.com/default_character" AND '
        'resource.labels.service="speech.googleapis.com"'
    )
    
    requests_metric = (
        'metric.type="serviceruntime.googleapis.com/quota/allocation/usage" AND '
        'metric.labels.quota_metric="speech.googleapis.com/default_requests" AND '
        'resource.labels.service="speech.googleapis.com"'
    )
    
    try:
        # Get characters usage
        characters_response = monitor_client.list_time_series(
            name=project_name,
            filter=characters_metric,
            interval=interval,
            view=monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL
        )
        
        # Get requests usage
        requests_response = monitor_client.list_time_series(
            name=project_name,
            filter=requests_metric,
            interval=interval,
            view=monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL
        )
        
        return {
            "characters_used": extract_metric_value(characters_response),
            "requests_used": extract_metric_value(requests_response),
        }
        
    except Exception as e:
        print(f"[DEBUG] Monitoring API error: {e}")
        raise RuntimeError(f"Monitoring API error: {str(e)}")

def extract_metric_value(response) -> int:
    """Extract numeric value from monitoring API response"""
    print(f"[DEBUG] Extrac metric value: {response}")
    max_value = 0
    for series in response:
        for point in series.points:
            if point.value.WhichOneof("value") == "int64_value":
                max_value = max(max_value, int(point.value.int64_value))
    return max_value

def get_usage_stats(client):
    """Get usage stats"""
    if client is None:
        raise RuntimeError("TTS client is not initialized")
    
    try:
        cloud_data = get_real_time_quota(client)
        print(cloud_data['characters_used'])

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
            'characters_used': 0,
            'characters_remaining': FREE_TIER_LIMITS['characters'],
            'requests_used': 0,
            'requests_remaining': FREE_TIER_LIMITS['requests'],
            'month': datetime.now().strftime("%Y-%m"),
            'source': 'fallback'
        }
        
def print_usage() -> None:
    stats = get_usage_stats()
    source_note = "(Google Cloud data)" if stats['source'] == 'google_cloud' else "(local estimate)"
        
    print(f"\n📊 Usage for {stats['month']} {source_note}:")
    print(f"• Characters: {stats['characters_used']:,}/{FREE_TIER_LIMITS['characters']:,}")
    print(f"• Requests: {stats['requests_used']:,}/{FREE_TIER_LIMITS['requests']:,}")