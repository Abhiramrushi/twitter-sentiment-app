# Deployment Guide

This repository is designed to run locally using Docker and Docker Compose.

## Prerequisites

- Docker
- Docker Compose
- Python 3.11+ (for local development without Docker)

## Local Docker Deployment

1. Build and start services:
   ```bash
   docker compose up --build
   ```

2. Backend API available at:
   - `http://localhost:8000`

3. Streamlit frontend available at:
   - `http://localhost:8501`

## Local Python Deployment

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the backend:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. Start the frontend:
   ```bash
   streamlit run frontend/app.py
   ```
