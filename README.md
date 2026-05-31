# 🐦 Twitter Sentiment Analysis - Full Stack ML Application

🚀 Live Demo:
https://nagulapalli0204-ml-model.hf.space

A production-ready machine learning application that analyzes the sentiment of tweets using the BERTweet model. Built with FastAPI backend, Streamlit frontend, and containerized with Docker.

## 📋 Project Overview

This application implements the complete ML engineering pipeline:
- **Model**: BERTweet (BERT model trained specifically for Twitter)
- **Backend**: FastAPI REST API for inference
- **Frontend**: Streamlit web interface for user interaction
- **Deployment**: Docker containerization for cloud deployment

## 🎯 Features

- ✅ Real-time sentiment analysis (Positive, Negative, Neutral)
- ✅ Confidence scores and probability distribution
- ✅ Single tweet and batch analysis
- ✅ Analysis history tracking
- ✅ Health check endpoint
- ✅ CORS enabled for cross-origin requests
- ✅ Comprehensive error handling
- ✅ RESTful API documentation (Swagger UI)

## 📦 Project Structure

```
twitter-sentiment-app/
├── app/
│   └── main.py                 # FastAPI backend application
├── frontend/
│   └── app.py                  # Streamlit UI application
├── model/
│   └── bertweet_sentiment/    # Pre-trained BERTweet model files
│       ├── config.json
│       ├── model.safetensors
│       ├── tokenizer_config.json
│       ├── vocab.txt
│       ├── special_tokens_map.json
│       ├── bpe.codes
│       └── added_tokens.json
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Multi-stage Docker build
├── docker-compose.yml         # Docker Compose orchestration
└── README.md                  # This file
```

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Docker (for containerized deployment)
- pip package manager

### Local Development Setup

#### 1. **Clone/Setup the Repository**
```bash
cd twitter-sentiment-app
```

#### 2. **Create Virtual Environment** (Recommended)
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

#### 3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

#### 4. **Verify Model Files**
Ensure the model files are in `model/bertweet_sentiment/`:
- `config.json`
- `model.safetensors`
- `tokenizer_config.json`
- `vocab.txt`
- Other supporting files

### Running Locally

#### **Terminal 1: Start Backend API**
```bash
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **Main API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

#### **Terminal 2: Start Frontend UI**
```bash
cd frontend
streamlit run app.py
```

The UI will open at: http://localhost:8501

### Testing the API

#### Using Postman/cURL

**Health Check:**
```bash
curl http://localhost:8000/health
```

**Single Prediction:**
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "I love this amazing product! #happy"}'
```

**Batch Prediction:**
```bash
curl -X POST http://localhost:8000/predict-batch \
  -H "Content-Type: application/json" \
  -d '["Great day!", "This is terrible", "It is okay"]'
```

#### Using Python
```python
import requests

# Single prediction
response = requests.post("http://localhost:8000/predict", 
    json={"text": "This product is amazing!"})
print(response.json())

# Expected response:
# {
#   "text": "This product is amazing!",
#   "sentiment": "Positive",
#   "confidence": 0.9876,
#   "label_scores": {
#     "Negative": 0.0012,
#     "Neutral": 0.0112,
#     "Positive": 0.9876
#   }
# }
```

---

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

**Build and Run Both Services:**
```bash
docker-compose up --build
```

This will:
- Build the backend image and run it on port 8000
- Build the frontend image and run it on port 8501
- Create a network for inter-service communication
- Start both services with health checks

**Access the Application:**
- Frontend UI: http://localhost:8501
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

**View Logs:**
```bash
docker-compose logs -f
```

**Stop Services:**
```bash
docker-compose down
```

### Using Docker (Individual Services)

**Build Backend Image:**
```bash
docker build -t sentiment-api:latest --target backend .
```

**Run Backend Container:**
```bash
docker run -p 8000:8000 \
  -v $(pwd)/model:/app/model \
  sentiment-api:latest
```

**Build Frontend Image:**
```bash
docker build -t sentiment-ui:latest --target frontend .
```

**Run Frontend Container:**
```bash
docker run -p 8501:8501 \
  --network host \
  sentiment-ui:latest
```

---

## 📊 API Endpoints

### 1. **GET /health**
Health check endpoint for monitoring

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "device": "cuda" or "cpu"
}
```

### 2. **POST /predict**
Single tweet sentiment analysis

**Request:**
```json
{
  "text": "I love this amazing product! #happy"
}
```

**Response:**
```json
{
  "text": "I love this amazing product! #happy",
  "sentiment": "Positive",
  "confidence": 0.9876,
  "label_scores": {
    "Negative": 0.0012,
    "Neutral": 0.0112,
    "Positive": 0.9876
  }
}
```

### 3. **POST /predict-batch**
Batch sentiment analysis (up to 100 tweets)

**Request:**
```json
["Great day!", "This is terrible", "It is okay"]
```

**Response:**
```json
{
  "predictions": [
    {
      "text": "Great day!",
      "sentiment": "Positive",
      "confidence": 0.95,
      "label_scores": {...}
    },
    ...
  ]
}
```

---

## 🌐 Cloud Deployment

### Deploy to Render

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

2. **Create Render Account** at https://render.com

3. **Create New Web Service**
   - Connect GitHub repository
   - Select Docker as environment
   - Configure:
     - **Build Command**: Leave default
     - **Start Command**: Leave default
     - **Port**: 8000 (for backend)

4. **Deploy**
   - Render will automatically build and deploy
   - Your API will be available at: `https://your-service.onrender.com`

5. **Update Frontend** (if deploying separately)
   - Create another Web Service for frontend
   - Set environment variable **API_BASE_URL** to your deployed backend URL (e.g., `https://your-backend.onrender.com`)
   - The Streamlit UI also lets you override the URL via the sidebar for testing

### Deploy to AWS EC2 (Free Tier)

1. Launch an EC2 instance (Ubuntu 22.04)
2. SSH into instance
3. Install Docker:
   ```bash
   sudo apt update
   sudo apt install docker.io
   sudo usermod -aG docker $USER
   ```
4. Clone repository and deploy:
   ```bash
   docker-compose up -d
   ```

---

## 📈 Model Information

**Model**: BERTweet
- **Architecture**: BERT base model fine-tuned on Twitter data
- **Languages**: English
- **Classes**: 3 (Negative, Neutral, Positive)
- **Input**: Text (max 280 characters - Twitter limit)
- **Output**: Sentiment label + confidence scores

**Performance**:
- Accuracy: ~90%+ on Twitter sentiment tasks
- Inference Time: ~100-200ms per tweet
- Model Size: ~500MB

---

## 🔧 Troubleshooting

### Issue: "Model not loaded"
- **Solution**: Verify model files exist in `model/bertweet_sentiment/`
- Check file permissions
- Ensure `config.json` is present

### Issue: "Cannot connect to API"
- **Solution**: Ensure backend is running on port 8000
- Check firewall settings
- Verify `PYTHONUNBUFFERED=1` environment variable

### Issue: "Out of memory" (CUDA)
- **Solution**: The model will automatically fall back to CPU
- Reduce batch size
- Clear GPU cache: `torch.cuda.empty_cache()`

### Issue: Frontend cannot find backend
- **Solution**: Update API URL in Streamlit sidebar
- Ensure both containers are on the same network (Docker Compose)
- Check firewall/CORS settings

---

## 📝 Model Classes & Sentiment Mapping

| Class Index | Label | Emoji |
|------------|-------|-------|
| 0 | Negative | 😢 |
| 1 | Neutral | 😐 |
| 2 | Positive | 😊 |

---

## 🎓 Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/)
- [Docker Documentation](https://docs.docker.com/)
- [BERTweet Paper](https://arxiv.org/abs/2005.10200)

---

## 📋 Checklist for Deployment

- [ ] Model files present in `model/bertweet_sentiment/`
- [ ] All dependencies installed from `requirements.txt`
- [ ] Backend tested locally with Postman/cURL
- [ ] Frontend tested locally and connects to backend
- [ ] Docker images build successfully
- [ ] Docker Compose services start without errors
- [ ] Health check endpoint returns 200 OK
- [ ] Git repository initialized and pushed
- [ ] Cloud platform account created (Render/AWS)
- [ ] Application deployed to production URL
- [ ] Public URL working and accessible

---

## 🚀 Performance Optimization Tips

1. **GPU Support**: Install CUDA for faster inference
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

2. **Model Caching**: The model is loaded once on startup for efficiency

3. **Batch Processing**: Use `/predict-batch` for multiple tweets to maximize throughput

4. **Monitoring**: Add logging for production tracking
   ```python
   import logging
   logger = logging.getLogger(__name__)
   ```

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review API logs: `docker-compose logs backend`
3. Check frontend logs: `docker-compose logs frontend`
4. Review Streamlit terminal output

---

## 📄 License

This project is created for educational purposes.

---

## 🎯 Next Steps

1. **Test Locally**: Run `docker-compose up` and test all endpoints
2. **Deploy**: Push to GitHub and deploy to Render/AWS
3. **Monitor**: Set up logging and monitoring
4. **Optimize**: Profile and optimize inference time
5. **Scale**: Implement caching and load balancing if needed

---

**Happy Analyzing! 🐦**
