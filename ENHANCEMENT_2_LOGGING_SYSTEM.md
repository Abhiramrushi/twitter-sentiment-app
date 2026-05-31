# Enhancement 2: Logging System

## Overview

This enhancement adds comprehensive logging and analytics tracking to both the backend API and frontend interface. The system logs all predictions, API performance metrics, and errors to structured files for later analysis and monitoring.

## What's New

### Backend (`app/main.py`)

- **Prediction Logging**: Every sentiment prediction is logged with timestamp, text, sentiment, confidence, threshold, and whether it met the threshold
- **Performance Logging**: Each API endpoint request logs response time, status code, HTTP method, and endpoint
- **Error Logging**: All exceptions are captured with full traceback, error type, and endpoint information
- **New Endpoint**: `GET /logs` returns current logging statistics

### Logging Utilities (`app/logging_config.py`)

- **`setup_logger()`**: Creates logger with console (colored) and file handlers
- **`log_prediction()`**: Logs prediction data to `predictions.jsonl`
- **`log_performance()`**: Logs API performance to `performance.jsonl`
- **`log_error()`**: Logs errors to `errors_*.log`
- **`get_log_stats()`**: Returns statistics on logged data
- **Rotating File Handlers**: Automatic log rotation at 10MB with 5 backups

### Frontend (`frontend/app.py`)

- **User Interaction Logging**: All analysis requests, completions, and errors are logged
- **API Health Check Logging**: Startup and health check events are tracked
- **Error Tracking**: User-facing errors and API failures are logged
- **Frontend Log File**: Interactions stored in `logs/frontend_interactions.log`

## Log File Locations

All logs are stored in the `logs/` directory:

```
logs/
├── api_YYYY-MM-DD.log              # General API operations (rotating, 10MB max, 5 backups)
├── predictions.jsonl               # Prediction analytics (JSON Lines format)
├── performance.jsonl               # API performance metrics (JSON Lines format)
├── errors_YYYY-MM-DD.log           # Error details (rotating, 10MB max, 5 backups)
└── frontend_interactions.log       # Frontend user interactions
```

## Log Data Formats

### Predictions (predictions.jsonl)

Each line is a JSON object:

```json
{
  "timestamp": "2024-05-28T14:30:22.123456",
  "user_id": "anonymous",
  "text": "I love this amazing product! #happy",
  "sentiment": "Positive",
  "confidence": 0.9234,
  "threshold": 0.7,
  "meets_threshold": true,
  "api_version": "1.0"
}
```

### Performance (performance.jsonl)

Each line is a JSON object:

```json
{
  "timestamp": "2024-05-28T14:30:22.456789",
  "endpoint": "/predict",
  "method": "POST",
  "status_code": 200,
  "response_time_ms": 145.32,
  "user_id": "anonymous"
}
```

### Errors (errors_YYYY-MM-DD.log)

Each line is a JSON object:

```json
{
  "timestamp": "2024-05-28T14:30:23.789012",
  "error_type": "HTTPException",
  "error_message": "Text cannot be empty",
  "endpoint": "/predict",
  "user_id": "anonymous",
  "traceback": "Traceback (most recent call last):\n  ..."
}
```

### Frontend Interactions (frontend_interactions.log)

Plain text format:

```
2024-05-28 14:30:22,123 - INFO - Streamlit app started - Connected to http://localhost:8000
2024-05-28 14:30:24,456 - INFO - API health check: OK
2024-05-28 14:30:25,789 - INFO - Single analysis started: 'I love this amazing product...'
2024-05-28 14:30:26,234 - INFO - Prediction successful - Sentiment: Positive, Confidence: 0.9234
2024-05-28 14:30:28,567 - INFO - Batch analysis started with 5 tweets
```

## Usage Examples

### Using the Logging System

The logging is **automatic** - no additional configuration needed:

```python
# All logging happens automatically when endpoints are called
# Example: Single prediction with logging
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "I love this!", "threshold": 0.7}'

# View logs
GET http://localhost:8000/logs
```

Response:
```json
{
  "logs_directory": "./logs",
  "total_predictions": 42,
  "total_errors": 2,
  "performance_entries": 47,
  "api_log_size_mb": 1.23,
  "last_updated": "2024-05-28T14:35:00.000000"
}
```

### Analyzing Logs in Python

```python
import json
from pathlib import Path

# Read predictions
with open("logs/predictions.jsonl", "r") as f:
    predictions = [json.loads(line) for line in f]

# Filter by sentiment
positive = [p for p in predictions if p["sentiment"] == "Positive"]
print(f"Total positive: {len(positive)}")

# Calculate average confidence
avg_confidence = sum(p["confidence"] for p in predictions) / len(predictions)
print(f"Average confidence: {avg_confidence:.4f}")

# Read performance metrics
with open("logs/performance.jsonl", "r") as f:
    perf = [json.loads(line) for line in f]

# Calculate average response time
avg_time = sum(p["response_time_ms"] for p in perf) / len(perf)
print(f"Average response time: {avg_time:.2f}ms")
```

### Real-Time Monitoring

```python
# Quick stats check
curl http://localhost:8000/logs | python -m json.tool

# Tail frontend logs
tail -f logs/frontend_interactions.log

# Watch performance metrics
watch -n 5 'tail -20 logs/performance.jsonl | python -m json.tool'
```

## API Reference

### GET /logs

Returns current logging statistics.

**Response:**
```json
{
  "logs_directory": "./logs",
  "total_predictions": 0,
  "total_errors": 0,
  "performance_entries": 0,
  "api_log_size_mb": 0.0,
  "last_updated": null
}
```

**Use Cases:**
- Monitor prediction volume
- Track error count
- Check API log file size
- Verify logging is working

## Configuration

### Logging Levels

Backend logs are set to `INFO` level by default. To change:

```python
# In app/main.py
from app.logging_config import setup_logger
logger = setup_logger(__name__, logging.DEBUG)  # More verbose
```

### Log Rotation

Current settings (in `app/logging_config.py`):
- Max file size: 10MB
- Number of backups: 5 (keeps last 50MB of logs)

To change:
```python
file_handler = logging.handlers.RotatingFileHandler(
    API_LOG_FILE,
    maxBytes=20*1024*1024,  # 20MB instead of 10MB
    backupCount=10          # Keep 10 backups instead of 5
)
```

## Benefits

1. **Analytics**: Understand usage patterns and prediction distribution
2. **Performance Monitoring**: Track response times per endpoint
3. **Debugging**: Full traceback for errors with context
4. **Compliance**: Audit trail of all predictions
5. **Optimization**: Identify slow endpoints or high error rates
6. **User Support**: Investigate specific predictions from frontend logs

## Testing Logging

### Test Backend Logging

```bash
# 1. Start backend
uvicorn app.main:app --reload

# 2. Make predictions
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "Great product!", "threshold": 0.5}'

# 3. Check logs
curl http://localhost:8000/logs

# 4. View log files
cat logs/predictions.jsonl
tail logs/performance.jsonl
```

### Test Frontend Logging

```bash
# 1. Start backend and frontend
uvicorn app.main:app --reload
streamlit run frontend/app.py

# 2. Use frontend to analyze tweets

# 3. Monitor logs in real-time
tail -f logs/frontend_interactions.log
```

## Log Analysis Scripts

### Count Sentiments

```python
import json
from collections import Counter

with open("logs/predictions.jsonl", "r") as f:
    predictions = [json.loads(line) for line in f]

sentiments = Counter(p["sentiment"] for p in predictions)
print(sentiments)
# Output: Counter({'Positive': 45, 'Neutral': 30, 'Negative': 15})
```

### Find Slow Requests

```python
import json

with open("logs/performance.jsonl", "r") as f:
    perf = [json.loads(line) for line in f]

slow = sorted(perf, key=lambda x: x["response_time_ms"], reverse=True)[:5]
for item in slow:
    print(f"{item['endpoint']}: {item['response_time_ms']:.2f}ms")
```

### Error Summary

```python
import json
from collections import Counter

with open("logs/errors_*.log", "r") as f:
    errors = [json.loads(line) for line in f]

error_types = Counter(e["error_type"] for e in errors)
print(error_types)
```

## Production Considerations

1. **Disk Space**: Monitor `logs/` directory size
   - Logs auto-rotate at 10MB per file
   - Keep approximately 50MB for concurrent logs

2. **Performance Impact**: Logging has minimal overhead
   - File I/O happens asynchronously
   - Rotate large files automatically

3. **Security**: Logs contain text content
   - Sensitive data in logs should be redacted
   - Store logs securely in production

4. **Retention Policy**: Define how long to keep logs
   - Example: Keep 30 days of logs, then archive
   - Use `cron` job to clean old logs

```bash
# Clean logs older than 30 days
find logs/ -name "*.log" -mtime +30 -delete
find logs/ -name "*.jsonl" -mtime +30 -delete
```

## Troubleshooting

### No Logs Being Created

```bash
# Check directory exists
ls -la logs/

# Check file permissions
chmod 755 logs/
```

### Logs Not Updating

```bash
# Verify app is running
curl http://localhost:8000/health

# Check if predictions are being made
tail -f logs/predictions.jsonl
```

### Logs Getting Too Large

```bash
# Check file size
du -h logs/

# Manually rotate if needed
# Old files are moved to api_*.log.1, api_*.log.2, etc.
```

## Next Steps

With logging in place, you can:
1. Integrate with monitoring tools (Prometheus, Grafana)
2. Set up alerts for high error rates
3. Create dashboards for prediction analytics
4. Implement log aggregation (ELK Stack)
5. Export logs to data warehouse for analysis

## Summary

Enhancement 2 provides comprehensive logging infrastructure for:
- ✅ Tracking every prediction with full context
- ✅ Monitoring API performance per endpoint
- ✅ Capturing and analyzing errors
- ✅ Recording frontend user interactions
- ✅ Providing `/logs` endpoint for quick stats
- ✅ Automatic log rotation and cleanup

All logging is automatic and requires zero configuration to start working.
