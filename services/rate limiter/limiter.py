from flask import Flask, jsonify, request
import time
import requests

app = Flask(__name__)

class Limiter:
    def __init__(self):
        # putting this up as a temporary limit for now
        self.limit = 10

    def fetch_epoch(self, counter_url):
        response = requests.get(f"{counter_url}/validate")
        response.raise_for_status()
        return response.json()["epoch_start"]
    
limiter = Limiter()
COUNTER_URL = "http://127.0.0.1:5001"

@app.route("/test-epoch", methods=["GET"])
def test_epoch():
    try:
        epoch = limiter.fetch_epoch(COUNTER_URL)
        return jsonify({
            "epoch_start": epoch,
            "status": "ok"
        })
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

if __name__ == "__main__":
    app.run(port=5002, debug=True)