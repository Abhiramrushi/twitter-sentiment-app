import requests

API_URL = "http://localhost:8000/predict"

def test_single_prediction():
    payload = {
        "text": "I love how fast this works!",
        "threshold": 0.5
    }
    response = requests.post(API_URL, json=payload)
    print("Status code:", response.status_code)
    print("Response:", response.json())

if __name__ == "__main__":
    test_single_prediction()
