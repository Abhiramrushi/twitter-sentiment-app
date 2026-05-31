# TODO - Twitter Sentiment App (Production Capstone)

## Plan Approval
- [x] User approved Phase 1–4 production alignment approach.

## Phase 1: Model Packaging & Serialization
- [x] Verify backend model/tokenizer load paths work in container without relying on docker volume mounts.
- [x] Add clear startup validation/logging if model files are missing.

## Phase 2: Backend API
- [x] Confirm monitoring increments correctly for success/failure and metrics-summary fields match frontend usage.
- [x] Tighten error handling (400/500) and ensure response schema consistency.

## Phase 3: Frontend Integration
- [x] Make Streamlit backend URL configurable via environment variable (for deployment).
- [x] Improve frontend error display using backend response body.

## Phase 4: Docker & Deployment
- [x] Ensure Docker builds work for cloud (backend service start without volumes).
- [x] Update README/DEPLOYMENT docs with concrete Render/Railway instructions + required env vars.

## Verification
- [ ] Run `docker-compose up --build`
- [ ] Test: `GET /health`, `POST /predict`, `POST /predict-batch`
- [ ] Launch Streamlit and confirm predictions
- [ ] Run/verify `test_api.py` if present

