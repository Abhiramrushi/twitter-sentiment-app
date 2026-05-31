"""
Monitoring and Metrics for Twitter Sentiment Analysis
Provides Prometheus-compatible metrics for real-time monitoring
"""

from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest
from datetime import datetime
import time

# Create a custom registry to avoid conflicts
REGISTRY = CollectorRegistry()

# ============================================================================
# COUNTERS - Track cumulative counts
# ============================================================================

# Total predictions made
predictions_total = Counter(
    'sentiment_predictions_total',
    'Total number of sentiment predictions',
    ['sentiment', 'threshold_pass'],
    registry=REGISTRY
)

# Total API requests by endpoint
api_requests_total = Counter(
    'api_requests_total',
    'Total API requests',
    ['endpoint', 'method', 'status_code'],
    registry=REGISTRY
)

# Total errors by type
errors_total = Counter(
    'sentiment_analysis_errors_total',
    'Total errors during sentiment analysis',
    ['error_type', 'endpoint'],
    registry=REGISTRY
)

# ============================================================================
# HISTOGRAMS - Track distributions (timing, confidence scores, etc.)
# ============================================================================

# Response time distribution (in seconds)
request_duration_seconds = Histogram(
    'sentiment_request_duration_seconds',
    'Time spent processing sentiment request',
    ['endpoint', 'method'],
    buckets=(0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0),
    registry=REGISTRY
)

# Confidence score distribution
confidence_score = Histogram(
    'sentiment_confidence_score',
    'Distribution of prediction confidence scores',
    ['sentiment'],
    buckets=(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
    registry=REGISTRY
)

# Batch size distribution
batch_size = Histogram(
    'batch_analysis_size',
    'Number of texts in batch analysis',
    buckets=(1, 5, 10, 20, 50, 100),
    registry=REGISTRY
)

# ============================================================================
# GAUGES - Track current state (instantaneous values)
# ============================================================================

# Currently loaded model status (1 = loaded, 0 = not loaded)
model_loaded = Gauge(
    'model_loaded',
    'Whether the ML model is currently loaded (1=yes, 0=no)',
    registry=REGISTRY
)

# Active requests in flight
active_requests = Gauge(
    'api_requests_in_flight',
    'Number of API requests currently being processed',
    ['endpoint'],
    registry=REGISTRY
)

# Error rate (percentage of failed requests in last window)
error_rate_percent = Gauge(
    'sentiment_error_rate_percent',
    'Percentage of requests that resulted in errors',
    registry=REGISTRY
)

# Last prediction timestamp
last_prediction_timestamp = Gauge(
    'last_prediction_timestamp_seconds',
    'Unix timestamp of last successful prediction',
    registry=REGISTRY
)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

# Python-side summary counters (kept in sync with Prometheus metrics)
TOTAL_PREDICTIONS = 0
TOTAL_API_REQUESTS = 0
TOTAL_ERRORS = 0
LAST_PREDICTION_TS = None

def record_prediction(sentiment: str, confidence: float, meets_threshold: bool):
    """
    Record a successful prediction
    
    Args:
        sentiment: Predicted sentiment (Positive, Negative, Neutral)
        confidence: Confidence score (0-1)
        meets_threshold: Whether prediction met threshold
    """
    # Record prediction counter
    threshold_status = "pass" if meets_threshold else "fail"
    predictions_total.labels(sentiment=sentiment, threshold_pass=threshold_status).inc()
    
    # Record confidence distribution
    confidence_score.labels(sentiment=sentiment).observe(confidence)
    
    # Update last prediction timestamp
    last_prediction_timestamp.set(time.time())
    global TOTAL_PREDICTIONS, LAST_PREDICTION_TS
    TOTAL_PREDICTIONS += 1
    LAST_PREDICTION_TS = time.time()


def record_api_request(endpoint: str, method: str, status_code: int, duration_seconds: float):
    """
    Record API request metrics
    
    Args:
        endpoint: API endpoint path
        method: HTTP method (GET, POST, etc.)
        status_code: Response status code
        duration_seconds: Request duration in seconds
    """
    # Record request counter
    api_requests_total.labels(endpoint=endpoint, method=method, status_code=status_code).inc()
    global TOTAL_API_REQUESTS
    TOTAL_API_REQUESTS += 1
    
    # Record request duration
    request_duration_seconds.labels(endpoint=endpoint, method=method).observe(duration_seconds)


def record_batch_analysis(batch_size_count: int, metrics: dict):
    """
    Record batch analysis metrics
    
    Args:
        batch_size_count: Number of items in batch
        metrics: Dict with results, stats, etc.
    """
    batch_size.observe(batch_size_count)
    
    # Record individual predictions from batch
    if 'predictions' in metrics:
        for pred in metrics['predictions']:
            sentiment = pred.get('sentiment')
            confidence = pred.get('confidence', 0)
            meets_threshold = pred.get('meets_threshold', False)
            record_prediction(sentiment, confidence, meets_threshold)


def record_error(error_type: str, endpoint: str):
    """
    Record error occurrence
    
    Args:
        error_type: Type of error (e.g., HTTPException, ValueError)
        endpoint: Endpoint where error occurred
    """
    errors_total.labels(error_type=error_type, endpoint=endpoint).inc()
    global TOTAL_ERRORS
    TOTAL_ERRORS += 1


def set_model_loaded(is_loaded: bool):
    """
    Update model loaded status
    
    Args:
        is_loaded: True if model is loaded, False otherwise
    """
    model_loaded.set(1 if is_loaded else 0)


def update_error_rate(error_count: int, total_requests: int):
    """
    Update error rate gauge
    
    Args:
        error_count: Total errors
        total_requests: Total requests
    """
    if total_requests > 0:
        rate = (error_count / total_requests) * 100
        error_rate_percent.set(rate)
    else:
        error_rate_percent.set(0)


def get_metrics():
    """
    Get all metrics in Prometheus text format
    
    Returns:
        Prometheus-compatible metrics string
    """
    return generate_latest(REGISTRY)


def get_metrics_summary() -> dict:
    """
    Get human-readable summary of key metrics
    
    Returns:
        Dict with summary statistics
    """
    summary = {
        "timestamp": datetime.now().isoformat(),
        "model_loaded": bool(model_loaded.collect()[0].samples[0].value) if model_loaded.collect() else False,
        "error_rate_percent": float(error_rate_percent.collect()[0].samples[0].value) if error_rate_percent.collect() else 0.0,
        "counters": {
            "total_predictions": TOTAL_PREDICTIONS,
            "total_api_requests": TOTAL_API_REQUESTS,
            "total_errors": TOTAL_ERRORS,
        },
        "last_prediction": datetime.fromtimestamp(LAST_PREDICTION_TS).isoformat() if LAST_PREDICTION_TS else None
    }
    return summary


# ============================================================================
# CONTEXT MANAGER FOR TIMING REQUESTS
# ============================================================================

class monitor_request:
    """Context manager to automatically record request timing"""
    
    def __init__(self, endpoint: str, method: str = "POST"):
        self.endpoint = endpoint
        self.method = method
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        active_requests.labels(endpoint=self.endpoint).inc()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        active_requests.labels(endpoint=self.endpoint).dec()
        
        if exc_type is None:
            status_code = 200
        else:
            status_code = 500
        
        record_api_request(self.endpoint, self.method, status_code, duration)
        
        return False
