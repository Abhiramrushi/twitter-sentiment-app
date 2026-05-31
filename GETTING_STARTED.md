# Getting Started

## Setup

1. Create a Python environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Run Locally

1. Start the backend:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. Start the Streamlit frontend:
   ```bash
   streamlit run frontend/app.py
   ```

3. Open the frontend in your browser at `http://localhost:8501`.

## Notes

- Place the model files in `model/bertweet_sentiment/`.
- Use `docker compose up --build` to run both services in containers.
