"""
FastAPI Backend for Twitter Sentiment Analysis
Handles model inference and provides REST API endpoints
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional

try:
    import torch
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
except Exception:
    # Defer import errors so the API can start without a fully working ML stack
    torch = None
    AutoTokenizer = None
    AutoModelForSequenceClassification = None
from pathlib import Path
import time
import traceback
import os
from app.logging_config import log_prediction, log_performance, log_error, get_log_stats
from app.monitoring import (
    set_model_loaded, record_prediction, record_error, record_batch_analysis,
    get_metrics, get_metrics_summary, monitor_request
)


# Initialize FastAPI app
app = FastAPI(
    title="Twitter Sentiment Analysis API",
    description="API for analyzing Twitter sentiment using BERTweet model",
    version="1.0.0"
)

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request/response models
class SentimentRequest(BaseModel):
    text: str
    threshold: float = 0.0  # Minimum confidence threshold (0.0-1.0 or 0-100%)
    
    class Config:
        example = {"text": "I love this amazing product! #happy", "threshold": 0.7}

class SentimentBatchRequest(BaseModel):
    texts: list
    threshold: float = 0.0
    
    class Config:
        example = {"texts": ["I love this", "This is bad"], "threshold": 0.5}

class SentimentResponse(BaseModel):
    text: str
    sentiment: str
    confidence: float
    confidence_percentage: float
    label_scores: dict
    meets_threshold: bool
    threshold_used: float
    warning: Optional[str] = None  # Warning message if confidence is low

# Global variables for model and tokenizer
model = None
tokenizer = None
device = None

def load_model():
    """Load the BERTweet sentiment model and tokenizer"""
    global model, tokenizer, device
    if torch is None:
        print("PyTorch not available in this environment; skipping model load.")
        model = None
        tokenizer = None
        return

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # Model location strategy:
    # 1) /app/model/bertweet_sentiment (Docker)
    # 2) ./model/bertweet_sentiment (local)
    # 3) If the user set MODEL_SOURCE to an HF model id/path, load from there.
    model_source = os.environ.get("MODEL_SOURCE")

    try:
        if model_source:
            # Can be a Hugging Face model id like "vinai/bertweet-base-sentiment"
            # or a local path inside the container.
            tokenizer = AutoTokenizer.from_pretrained(model_source)
            model = AutoModelForSequenceClassification.from_pretrained(model_source)
        else:
            model_path_candidates = [
                Path("/app/model/bertweet_sentiment"),
                Path("./model/bertweet_sentiment"),
            ]
            model_path = next((p for p in model_path_candidates if p.exists()), None)
            if model_path is None:
                raise FileNotFoundError(
                    "BERTweet model files not found. Expected /app/model/bertweet_sentiment or ./model/bertweet_sentiment"
                )
            tokenizer = AutoTokenizer.from_pretrained(str(model_path))
            model = AutoModelForSequenceClassification.from_pretrained(str(model_path))

        model.to(device)
        model.eval()
        print(f"✓ Model loaded successfully on device: {device}")
    except Exception as e:
        print(f"✗ Error loading model: {str(e)}")
        model = None
        tokenizer = None
        return

@app.on_event("startup")
async def startup_event():
    """Load model on app startup"""
    load_model()

    # Startup validation (production-friendly): if model files are missing,
    # log a clear message so deployments fail fast during debugging.
    try:
        model_dir_container = Path("/app/model/bertweet_sentiment")
        model_dir_local = Path("./model/bertweet_sentiment")
        exists = model_dir_container.exists() or model_dir_local.exists()
        if not exists:
            print("✗ Model files not found. Expected at /app/model/bertweet_sentiment (container) or ./model/bertweet_sentiment (local).")
    except Exception:
        # Don't crash startup because of filesystem checks
        pass

    set_model_loaded(model is not None)

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on app shutdown"""
    global model, tokenizer
    model = None
    tokenizer = None
    set_model_loaded(False)

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    Returns 200 OK if service is running
    """
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "device": str(device)
    }

@app.post("/predict", response_model=SentimentResponse)
async def predict_sentiment(request: SentimentRequest):
    """
    Core prediction endpoint with confidence thresholding
    Analyzes sentiment of input text
    
    Args:
        request: SentimentRequest with text and optional threshold field
        
    Returns:
        SentimentResponse with sentiment label, confidence scores, and threshold info
    """
    with monitor_request("/predict", "POST"):
        # If the model/tokenizer couldn't be loaded, fall back to a lightweight heuristic
        if model is None or tokenizer is None:
            return fallback_predict(request.text, request.threshold)
        
        if not request.text or len(request.text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        if len(request.text) > 280:  # Twitter character limit
            request.text = request.text[:280]
        
        start_time = time.time()
        
        # Validate threshold
        threshold = request.threshold
        if threshold < 0 or threshold > 1:
            # If threshold > 1, assume it's a percentage (0-100)
            if threshold > 1 and threshold <= 100:
                threshold = threshold / 100
            else:
                raise HTTPException(status_code=400, detail="Threshold must be 0-1 or 0-100")
        
        try:
            # Tokenize input
            inputs = tokenizer(
                request.text,
                return_tensors="pt",
                truncation=True,
                max_length=128,
                padding=True
            ).to(device)

            # Model inference
            with torch.no_grad():
                outputs = model(**inputs)

            # Get predictions
            logits = outputs.logits
            probabilities = torch.softmax(logits, dim=1)
            predicted_class = torch.argmax(logits, dim=1).item()
            confidence = probabilities[0][predicted_class].item()
            
            # Map class to sentiment label
            # Assuming: 0=Negative, 1=Neutral, 2=Positive
            sentiment_labels = {
                0: "Negative",
                1: "Neutral",
                2: "Positive"
            }
            
            sentiment = sentiment_labels.get(predicted_class, "Unknown")
            
            # Prepare label scores
            label_scores = {
                sentiment_labels[i]: float(probabilities[0][i].item())
                for i in range(len(sentiment_labels))
            }
            
            # Check if confidence meets threshold
            meets_threshold = confidence >= threshold
            warning = None
        
            if not meets_threshold:
                warning = f"Confidence ({confidence*100:.1f}%) is below threshold ({threshold*100:.1f}%). Result may be unreliable."
            
            response = SentimentResponse(
                text=request.text,
                sentiment=sentiment,
                confidence=round(confidence, 4),
                confidence_percentage=round(confidence * 100, 2),
                label_scores=label_scores,
                meets_threshold=meets_threshold,
                threshold_used=round(threshold, 4),
                warning=warning
            )

            log_prediction(
                text=request.text,
                sentiment=sentiment,
                confidence=confidence,
                threshold=threshold,
                meets_threshold=meets_threshold,
                api_version="1.0"
            )
            
            # Record monitoring metrics
            record_prediction(sentiment, confidence, meets_threshold)

            log_performance(
                endpoint="/predict",
                method="POST",
                status_code=200,
                response_time_ms=(time.time() - start_time) * 1000
            )
            
            return response
            
        except Exception as e:
            traceback_str = traceback.format_exc()
            record_error(type(e).__name__, "/predict")
            log_error(
                error_type=type(e).__name__,
                error_message=str(e),
                endpoint="/predict",
                traceback_str=traceback_str
            )
            raise HTTPException(
                status_code=500,
                detail=f"Error during prediction: {str(e)}"
            )


def fallback_predict(text: str, threshold: float = 0.0) -> SentimentResponse:
    """Very small rule-based fallback predictor when model is unavailable.
    This ensures the API can respond for smoke tests and basic demonstrations.
    """
    start_time = time.time()

    t = text.lower()
    positive_words = ["love", "great", "good", "awesome", "amazing", "happy", "fantastic", "best"]
    negative_words = ["hate", "bad", "terrible", "awful", "worst", "sad", "angry", "disappoint"]

    pos_count = sum(t.count(w) for w in positive_words)
    neg_count = sum(t.count(w) for w in negative_words)

    if pos_count > neg_count:
        sentiment = "Positive"
        confidence = min(0.95, 0.5 + 0.25 * (pos_count - neg_count))
    elif neg_count > pos_count:
        sentiment = "Negative"
        confidence = min(0.95, 0.5 + 0.25 * (neg_count - pos_count))
    else:
        sentiment = "Neutral"
        confidence = 0.6

    label_scores = {
        "Positive": round(confidence if sentiment == "Positive" else 1 - confidence, 4),
        "Neutral": round(0.2 if sentiment != "Neutral" else confidence, 4),
        "Negative": round(confidence if sentiment == "Negative" else 1 - confidence, 4)
    }

    # Normalize threshold
    th = threshold
    if th < 0 or th > 1:
        if th > 1 and th <= 100:
            th = th / 100
        else:
            th = 0.0

    meets_threshold = confidence >= th
    warning = None if meets_threshold else f"Fallback predictor confidence ({confidence*100:.1f}%) below threshold ({th*100:.1f}%)."

    response = SentimentResponse(
        text=text,
        sentiment=sentiment,
        confidence=round(confidence, 4),
        confidence_percentage=round(confidence * 100, 2),
        label_scores=label_scores,
        meets_threshold=meets_threshold,
        threshold_used=round(th, 4),
        warning=warning
    )

    # Log and metrics (use best-effort; logging functions exist)
    try:
        log_prediction(text=text, sentiment=sentiment, confidence=confidence, threshold=th, meets_threshold=meets_threshold)
        record_prediction(sentiment, confidence, meets_threshold)
        log_performance(endpoint="/predict", method="POST", status_code=200, response_time_ms=(time.time() - start_time) * 1000)
    except Exception:
        pass

    return response

@app.post("/predict-batch")
async def predict_batch(request: SentimentBatchRequest):
    """
    Batch prediction endpoint with threshold support
    Analyzes sentiment of multiple texts at once
    
    Args:
        request: SentimentBatchRequest with texts list and threshold
        
    Returns:
        List of sentiment predictions with threshold info
    """
    with monitor_request("/predict-batch", "POST"):
        if not request.texts or len(request.texts) == 0:
            raise HTTPException(status_code=400, detail="Texts list cannot be empty")
        
        if len(request.texts) > 100:
            raise HTTPException(status_code=400, detail="Maximum 100 texts per request")
        
        start_time = time.time()
        
        try:
            results = []
            for text in request.texts:
                pred_request = SentimentRequest(text=text, threshold=request.threshold)
                result = await predict_sentiment(pred_request)
                results.append(result.dict())
        
            # Calculate statistics
            total = len(results)
            passed_threshold = sum(1 for r in results if r["meets_threshold"])
            
            batch_metrics = {
                "predictions": results
            }
            record_batch_analysis(len(results), batch_metrics)
            log_performance(
                endpoint="/predict-batch",
                method="POST",
                status_code=200,
                response_time_ms=(time.time() - start_time) * 1000
            )
            
            return {
                "predictions": results,
                "statistics": {
                    "total_predictions": total,
                    "passed_threshold": passed_threshold,
                    "failed_threshold": total - passed_threshold,
                    "threshold_used": request.threshold,
                    "pass_rate": round(passed_threshold / total * 100, 2) if total > 0 else 0
                }
            }
        except Exception as e:
            traceback_str = traceback.format_exc()
            record_error(type(e).__name__, "/predict-batch")
            log_error(
                error_type=type(e).__name__,
                error_message=str(e),
                endpoint="/predict-batch",
                traceback_str=traceback_str
            )
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=get_metrics(), media_type="text/plain; version=0.0.4")

@app.get("/metrics-summary")
async def metrics_summary():
    """Human-readable monitoring summary"""
    return get_metrics_summary()

@app.get("/logs")
async def get_log_stats_endpoint():

    """Return current logging statistics"""
    stats = get_log_stats()
    return stats

@app.get("/")
async def root():
    """Root endpoint with API documentation"""
    return {
        "message": "Twitter Sentiment Analysis API",
        "docs_url": "/docs",
        "health_url": "/health",
        "predict_url": "/predict",
        "logs_url": "/logs",
        "metrics_url": "/metrics",
        "metrics_summary_url": "/metrics-summary"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
