# Multi-stage Dockerfile for Twitter Sentiment Analysis

# Stage 1: Base image with Python
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Stage 2: Backend (FastAPI)
FROM base as backend

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY model/ ./model/

# Expose port for API
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Stage 3: Frontend (Streamlit) - for Docker Compose
FROM base as frontend

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy frontend code
COPY frontend/ ./frontend/

# Expose port for Streamlit
EXPOSE 8501

# Configure Streamlit
RUN mkdir -p ~/.streamlit && \
    echo "[client]\nshowErrorDetails = true\n[logger]\nlevel = debug" > ~/.streamlit/config.toml

# Run Streamlit app
CMD ["streamlit", "run", "frontend/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
