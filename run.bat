@echo off
REM Start the backend and frontend for local development.
set PYTHONPATH=%~dp0
start cmd /k "uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
start cmd /k "streamlit run frontend/app.py"
