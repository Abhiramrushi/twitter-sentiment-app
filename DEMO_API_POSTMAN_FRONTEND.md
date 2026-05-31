# Demo: API (Postman) + Frontend (Browser)

## Goal
Show that:
1) The FastAPI backend responds correctly when called via **Postman**.
2) The Streamlit frontend can call the backend and display sentiment results in the browser.

---

## Step 1 — Start the backend (FastAPI)
1. Open a terminal.
2. Run:
   ```bash
   cd app && uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
3. (Optional) Open in browser:
   - Swagger UI: http://localhost:8000/docs
   - Health: http://localhost:8000/health

---

## Step 2 — Test API using Postman
### A) Health check
1. In Postman, create a request:
   - Method: **GET**
   - URL: `http://localhost:8000/health`
2. Click **Send**.
3. Expected output (example fields):
   - `status`: `healthy`
   - `model_loaded`: `true` (or `false` if fallback is used)
   - `device`: `cpu` or `cuda`

### B) Single tweet prediction
1. In Postman, create a request:
   - Method: **POST**
   - URL: `http://localhost:8000/predict`
2. Headers:
   - `Content-Type: application/json`
3. Body (raw JSON), e.g.:
   ```json
   {
     "text": "I love this app!",
     "threshold": 0.7
   }
   ```
4. Click **Send**.
5. Expected response JSON contains:
   - `sentiment`: `Positive` / `Negative` / `Neutral`
   - `confidence`, `confidence_percentage`
   - `label_scores` (Negative/Neutral/Positive)
   - `meets_threshold` (boolean)
   - `warning` (string, only if below threshold)

### C) (Optional) Batch prediction
1. Method: **POST**
2. URL: `http://localhost:8000/predict-batch`
3. Body, e.g.:
   ```json
   {
     "texts": ["Great day!", "This is terrible", "It is okay"],
     "threshold": 0.5
   }
   ```
4. Click **Send**.
5. Expected response contains:
   - `predictions`: list
   - `statistics`: `total_predictions`, `passed_threshold`, `failed_threshold`, `pass_rate`

---

## Step 3 — Start the frontend (Streamlit)
1. Open a second terminal.
2. Run:
   ```bash
   cd frontend && streamlit run app.py
   ```
3. Open the browser URL shown by Streamlit (commonly):
   - http://localhost:8501

---

## Step 4 — Use the frontend in the browser
1. In the Streamlit sidebar:
   - Ensure it shows **✅ API Connected**.
2. Go to **Single Analysis** tab.
3. Paste a tweet, e.g.:
   - `I love this app!`
4. Adjust the **Confidence Threshold** slider if needed.
5. Click **🔍 Analyze Sentiment**.
6. Confirm UI displays:
   - Sentiment badge (Positive/Negative/Neutral)
   - Confidence score + percentage
   - Threshold status (✅ Passed / ⚠️ Below Threshold)
   - Confidence breakdown + per-label progress

---

## Pass/Fail Criteria (what your demo must prove)
- Postman requests to `/health` and `/predict` return valid JSON.
- Streamlit UI successfully calls the backend and renders prediction results.
- The threshold behavior is visible (e.g., warning/status when confidence is below the chosen threshold).

