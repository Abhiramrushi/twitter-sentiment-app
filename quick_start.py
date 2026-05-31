import requests

BACKEND_URL = "http://localhost:8000/predict"

if __name__ == "__main__":
    text = "Streaming sentiment analysis is great."
    payload = {"text": text, "threshold": 0.6}
    response = requests.post(BACKEND_URL, json=payload)
    print(response.status_code)
    print(response.json())
