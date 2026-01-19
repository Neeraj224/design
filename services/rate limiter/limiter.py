from flask import Flask, jsonify, request
import time
import requests

HOME_URL = "http://127.0.0.1"
COUNTER_PORT = "5001"
COUNTER_URL = HOME_URL + ":" + COUNTER_PORT

app = Flask(__name__)

class Limiter:
    def __init__(self):
        # putting this up as a temporary limit for now
        self.limit = 10

    def fetch_epoch(self, counter_url):
        response = requests.get(f"{counter_url}/validate")
        response.raise_for_status()
        return response.json()["epoch_start"]
    
    def fetch_tokens(self, user_id):
        # our cache is the source of truth
        # over here - but when do we actually
        # update the cache?
        # and what about start-up situations?
        
        return
    
    def update_tokens(self, user_id):
        # how do we manage the updation of tokens?
        # an async call needs to be made every 5 minutes
        # (according to the rate calculations)
        # and will that be a process that runs in the background?
        return
    
    def build_record(self, request, counter_url):
        '''
            request format should be simply:
            {
                user_id: "xyz-0123456789",
                service: "get()"
            }
        '''
        # get user_id from JSON body
        data = request.json
        if not data or "user_id" not in data:
            raise ValueError("Missing user_id in request")
        
        user_id = data["user_id"]
        payload = {"user_id": user_id}
        
        # POST to stamper service
        response = requests.post(f"{counter_url}/stamp", json=payload)
        response.raise_for_status()
        
        return response.json()
    
limiter = Limiter()

@app.route("/get-epoch", methods=["GET"])
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

@app.route("/stamped-request", methods=["POST"])
def stamp_request():
    try:
        stamped_request = limiter.build_record(request, COUNTER_URL)
        return jsonify(stamped_request)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5002, debug=True)