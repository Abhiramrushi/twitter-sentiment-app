"""
Logging Configuration for Twitter Sentiment Analysis
Provides centralized logging for backend API
"""

import logging
import logging.handlers
from datetime import datetime
from pathlib import Path
import json
import sys

# Create logs directory if it doesn't exist
LOGS_DIR = Path("./logs")
LOGS_DIR.mkdir(exist_ok=True)

# Log file paths
API_LOG_FILE = LOGS_DIR / f"api_{datetime.now().strftime('%Y-%m-%d')}.log"
PREDICTION_LOG_FILE = LOGS_DIR / "predictions.jsonl"  # JSON Lines format
ERROR_LOG_FILE = LOGS_DIR / f"errors_{datetime.now().strftime('%Y-%m-%d')}.log"
PERFORMANCE_LOG_FILE = LOGS_DIR / "performance.jsonl"

class CustomFormatter(logging.Formatter):
    """Custom formatter with colors and better formatting"""
    
    grey = "\x1b[38;21m"
    blue = "\x1b[38;5;39m"
    yellow = "\x1b[38;5;226m"
    red = "\x1b[38;5;196m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    
    FORMATS = {
        logging.DEBUG: grey + "%(asctime)s - %(name)s - DEBUG - %(message)s" + reset,
        logging.INFO: blue + "%(asctime)s - %(name)s - INFO - %(message)s" + reset,
        logging.WARNING: yellow + "%(asctime)s - %(name)s - WARNING - %(message)s" + reset,
        logging.ERROR: red + "%(asctime)s - %(name)s - ERROR - %(message)s" + reset,
        logging.CRITICAL: bold_red + "%(asctime)s - %(name)s - CRITICAL - %(message)s" + reset,
    }
    
    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)

def setup_logger(name: str, level=logging.INFO) -> logging.Logger:
    """
    Setup logger with file and console handlers
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers = []
    
    # Console Handler (with colors)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(CustomFormatter())
    logger.addHandler(console_handler)
    
    # File Handler
    file_handler = logging.handlers.RotatingFileHandler(
        API_LOG_FILE,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(level)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    return logger

def log_prediction(
    text: str,
    sentiment: str,
    confidence: float,
    threshold: float = 0.0,
    meets_threshold: bool = True,
    user_id: str = "anonymous",
    api_version: str = "v1"
) -> None:
    """
    Log a prediction to JSONL file for analytics
    
    Args:
        text: Input text
        sentiment: Predicted sentiment
        confidence: Confidence score
        threshold: Threshold used
        meets_threshold: Did it pass threshold
        user_id: User identifier
        api_version: API version
    """
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id,
        "text": text[:100],  # First 100 chars
        "sentiment": sentiment,
        "confidence": round(confidence, 4),
        "threshold": round(threshold, 4),
        "meets_threshold": meets_threshold,
        "api_version": api_version
    }
    
    with open(PREDICTION_LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

def log_performance(
    endpoint: str,
    method: str,
    status_code: int,
    response_time_ms: float,
    user_id: str = "anonymous"
) -> None:
    """
    Log API performance metrics
    
    Args:
        endpoint: API endpoint path
        method: HTTP method (GET, POST, etc)
        status_code: Response status code
        response_time_ms: Response time in milliseconds
        user_id: User identifier
    """
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "endpoint": endpoint,
        "method": method,
        "status_code": status_code,
        "response_time_ms": round(response_time_ms, 2),
        "user_id": user_id
    }
    
    with open(PERFORMANCE_LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

def log_error(
    error_type: str,
    error_message: str,
    endpoint: str = None,
    user_id: str = "anonymous",
    traceback_str: str = None
) -> None:
    """
    Log error details
    
    Args:
        error_type: Type of error
        error_message: Error message
        endpoint: Endpoint where error occurred
        user_id: User identifier
        traceback_str: Full traceback string
    """
    error_logger = setup_logger("error_logger", logging.ERROR)
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "error_type": error_type,
        "error_message": error_message,
        "endpoint": endpoint,
        "user_id": user_id,
        "traceback": traceback_str
    }
    
    # Log to file
    with open(ERROR_LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")
    
    # Also log to logger
    error_logger.error(f"{error_type}: {error_message}")

def get_logs_directory() -> Path:
    """Get logs directory path"""
    return LOGS_DIR

def get_log_stats() -> dict:
    """
    Get statistics about logs
    
    Returns:
        Dictionary with log statistics
    """
    stats = {
        "logs_directory": str(LOGS_DIR),
        "total_predictions": 0,
        "total_errors": 0,
        "performance_entries": 0,
        "api_log_size_mb": 0.0,
        "last_updated": None
    }
    
    # Count predictions
    if PREDICTION_LOG_FILE.exists():
        with open(PREDICTION_LOG_FILE, "r") as f:
            stats["total_predictions"] = sum(1 for _ in f)
    
    # Count errors
    if ERROR_LOG_FILE.exists():
        with open(ERROR_LOG_FILE, "r") as f:
            stats["total_errors"] = sum(1 for _ in f)
    
    # Count performance entries
    if PERFORMANCE_LOG_FILE.exists():
        with open(PERFORMANCE_LOG_FILE, "r") as f:
            stats["performance_entries"] = sum(1 for _ in f)
    
    # Get file size
    if API_LOG_FILE.exists():
        stats["api_log_size_mb"] = round(API_LOG_FILE.stat().st_size / (1024*1024), 2)
        stats["last_updated"] = datetime.fromtimestamp(
            API_LOG_FILE.stat().st_mtime
        ).isoformat()
    
    return stats

# Initialize main logger
logger = setup_logger(__name__, logging.INFO)
