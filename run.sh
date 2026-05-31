#!/usr/bin/env bash
# Start backend and frontend for local development.
PYTHONPATH="$(pwd)"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
streamlit run frontend/app.py
