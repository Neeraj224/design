from flask import Flask, jsonify, request
import requests
import time

HOME_URL = "http://127.0.0.1"

COUNTER_PORT = "5001"
COUNTER_URL = HOME_URL + ":" + COUNTER_PORT

app = Flask(__name__)

class MockCacheService:
    def __init__(self):
        self.store = {}
        # and we also fetch the epoch start for the entire operation:
        response = requests.get(COUNTER_URL + "/validate")
        response.raise_for_status()
        self.epoch_start = response.json()["epoch_start"]
    
    def list_store(self):
        return self.store
    
    def get(self, key):
        if key in self.store:
            return self.store.get(key)
        else:
            return None

    def set(self, key, value):
        if key in self.store:
            self.store[key] = value
        else:
            # i know both are same for now, but we will
            # update this to be better
            self.store[key] = value

mockCache = MockCacheService()

@app.route("/peek-cache", methods=["GET"])
def list_cache():
    return jsonify(mockCache.list_store())

@app.route("/get-cache/<key>", methods=["GET"])
def get_key(key):
    response = mockCache.get(key)
    if response is None:
        return jsonify({"error": "Cache Miss"}), 404
    return jsonify(response)

@app.route("/set-cache/<key>", methods=["POST"])
def set_key(key):
    mockCache.set(key, request.json)
    return jsonify({"status": "OK"}), 200

if __name__ == "__main__":
    app.run(port=6001, debug=True)