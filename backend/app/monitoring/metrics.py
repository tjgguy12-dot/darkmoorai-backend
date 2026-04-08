"""
Metrics Module
Prometheus metrics for monitoring
"""

from prometheus_client import (
    Counter, Histogram, Gauge, Summary,
    generate_latest, CONTENT_TYPE_LATEST
)
import time
from typing import Dict, Any

# Initialize metrics
requests_total = Counter(
    'darkmoor_requests_total',
    'Total requests count',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'darkmoor_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint'],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10)
)

errors_total = Counter(
    'darkmoor_errors_total',
    'Total errors count',
    ['method', 'endpoint', 'error_type']
)

active_users = Gauge(
    'darkmoor_active_users',
    'Currently active users'
)

active_conversations = Gauge(
    'darkmoor_active_conversations',
    'Currently active conversations'
)

documents_processed = Counter(
    'darkmoor_documents_processed_total',
    'Total documents processed',
    ['status']
)

search_queries = Counter(
    'darkmoor_search_queries_total',
    'Total search queries',
    ['source']
)

api_calls = Counter(
    'darkmoor_api_calls_total',
    'Total API calls',
    ['service', 'endpoint']
)

api_latency = Histogram(
    'darkmoor_api_latency_seconds',
    'External API latency',
    ['service'],
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10)
)

cost_total = Counter(
    'darkmoor_cost_total_dollars',
    'Total API costs in USD',
    ['service']
)

queue_size = Gauge(
    'darkmoor_queue_size',
    'Background task queue size',
    ['queue']
)

database_pool_size = Gauge(
    'darkmoor_database_pool_size',
    'Database connection pool size'
)

database_connections_active = Gauge(
    'darkmoor_database_connections_active',
    'Active database connections'
)

cache_hit_ratio = Gauge(
    'darkmoor_cache_hit_ratio',
    'Cache hit ratio'
)

def setup_metrics():
    """
    Setup metrics collectors
    """
    # This runs at startup
    pass

def record_request(method: str, path: str, status: int, duration: float, user_id: str = None):
    """
    Record a request metric
    """
    endpoint = path.split('/')[3] if len(path.split('/')) > 3 else 'unknown'
    
    requests_total.labels(
        method=method,
        endpoint=endpoint,
        status=status
    ).inc()
    
    request_duration.labels(
        method=method,
        endpoint=endpoint
    ).observe(duration)

def increment_requests_total(method: str, path: str, status: int):
    """Increment requests counter"""
    endpoint = path.split('/')[3] if len(path.split('/')) > 3 else 'unknown'
    requests_total.labels(method=method, endpoint=endpoint, status=status).inc()

def observe_request_duration(method: str, path: str, duration: float):
    """Observe request duration"""
    endpoint = path.split('/')[3] if len(path.split('/')) > 3 else 'unknown'
    request_duration.labels(method=method, endpoint=endpoint).observe(duration)

def increment_errors_total(method: str, path: str, error_type: str = "unknown"):
    """Increment errors counter"""
    endpoint = path.split('/')[3] if len(path.split('/')) > 3 else 'unknown'
    errors_total.labels(method=method, endpoint=endpoint, error_type=error_type).inc()

def record_document_processed(status: str):
    """Record document processing status"""
    documents_processed.labels(status=status).inc()

def record_search_query(source: str):
    """Record search query"""
    search_queries.labels(source=source).inc()

def record_api_call(service: str, endpoint: str, duration: float = None):
    """Record external API call"""
    api_calls.labels(service=service, endpoint=endpoint).inc()
    if duration:
        api_latency.labels(service=service).observe(duration)

def record_cost(service: str, cost: float):
    """Record API cost"""
    cost_total.labels(service=service).inc(cost)

def update_active_users(count: int):
    """Update active users count"""
    active_users.set(count)

def update_queue_size(queue_name: str, size: int):
    """Update queue size metric"""
    queue_size.labels(queue=queue_name).set(size)

def update_database_pool(size: int, active: int):
    """Update database pool metrics"""
    database_pool_size.set(size)
    database_connections_active.set(active)

def update_cache_hit_ratio(ratio: float):
    """Update cache hit ratio"""
    cache_hit_ratio.set(ratio)

def get_metrics_snapshot() -> Dict[str, Any]:
    """
    Get current metrics snapshot
    """
    return {
        "requests_total": requests_total._value.get(),
        "errors_total": errors_total._value.get(),
        "active_users": active_users._value.get(),
        "documents_processed": documents_processed._value.get(),
        "search_queries": search_queries._value.get(),
        "api_calls": api_calls._value.get(),
        "cost_total": cost_total._value.get(),
        "queue_size": queue_size._value.get(),
        "database_pool_size": database_pool_size._value.get(),
        "cache_hit_ratio": cache_hit_ratio._value.get()
    }

def generate_metrics():
    """
    Generate Prometheus metrics
    """
    return generate_latest()