# Architecture Overview

This project is a Twitter Sentiment Analysis application built with a Python FastAPI backend and a Streamlit frontend.

## Components

- `app/main.py` - FastAPI backend serving sentiment predictions and health checks.
- `app/logging_config.py` - Central logging utilities for predictions, performance, and errors.
- `frontend/app.py` - Streamlit user interface for single and batch sentiment analysis.
- `model/bertweet_sentiment/` - Local Hugging Face model files for sentiment inference.
- `Dockerfile` - Multi-stage build for production-ready backend and frontend containers.
- `docker-compose.yml` - Local orchestration for backend and frontend services.

## Data Flow

1. User enters text in Streamlit UI.
2. Frontend sends a POST request to the FastAPI `/predict` or `/predict-batch` endpoint.
3. Backend tokenizes the text using BERTweet tokenizer and runs model inference.
4. Backend returns sentiment, confidence scores, and threshold status.
5. Frontend displays results and maintains history.

## Monitoring & Logging

- Logs are written to `logs/` using rotating file handlers.
- Predictions are stored in `predictions.jsonl` and performance events in `performance.jsonl`.
- Error logging captures runtime failures separately.
