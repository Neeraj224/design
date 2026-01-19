from flask import Flask, jsonify, request
import time
import requests

COUNTER_PORT = "5001"
CACHE_PORT = "6001"

HOME_URL = "http://127.0.0.1"
COUNTER_URL = HOME_URL + ":" + COUNTER_PORT
CACHE_URL = HOME_URL + ":" + CACHE_PORT

TOKEN_LIMIT = 10
# refill every 5 minutes = 5 * 60 = 300 seconds
REFILL_INTERVAL = 300
# we refill with only 1 token every interval
REFILL_AMOUNT = 1

app = Flask(__name__)

class Limiter:
    def __init__(self):
        # putting this up as a temporary limit for now
        self.limit = 10

    def fetch_epoch(self, counter_url):
        response = requests.get(f"{counter_url}/validate")
        response.raise_for_status()
        return response.json()["epoch_start"]
    
    def create_tokens(self, user_id):
        # we build our payload and create a last_refill_ts
        # which is last refilled timestamp for the user that tells
        # when was its token bucket last refilled
        payload = {
            "tokens": TOKEN_LIMIT,
            "last_refill_ts": time.time()
        }
        # call the set-cache API and send our payload so that we can
        # store it in the cache
        response = requests.post(CACHE_URL + "/set-cache/" + user_id, json = payload)
        return jsonify(response)
    
    def fetch_tokens(self, user_id):
        # see if we get anything for the user request
        response = requests.get(CACHE_URL + "/get-cache/" + user_id)
        print(response)
        # if we get a cache miss, we simply create new tokens for the user:
        if response.status_code == 404:
            print("Cache Miss; creating tokens for the user_id" + user_id)
            self.create_tokens(user_id=user_id)
        return response
    
    def update_tokens(self, user_id):
        """
        Update tokens in the cache for a given user based on
        elapsed time.
        """
        # first we fetch the current state from cache:
        response = requests.get(CACHE_URL + "/get-cache/" + user_id)
        if response.status_code == 404:
            print("Cache Miss; creating tokens for the user_id" + user_id)
            self.create_tokens(user_id=user_id)
            # no refill needed since we just created
            return
        
        response.raise_for_status()
        data = response.json()
        
        tokens = data["tokens"]
        last_refill_ts = data["last_refill_ts"]
        
        # now we calculate the elapsed time:
        current_time = time.time()
        elapsed_time = current_time - last_refill_ts
        
        # see how many tokens to add
        refill_count = int(elapsed_time // REFILL_INTERVAL) * REFILL_AMOUNT
        
        # now we only update cache if tokens are added
        if refill_count > 0:
            tokens = min(tokens + refill_count, TOKEN_LIMIT)
            last_refill_ts = current_time
            
            payload = {
                "tokens": tokens,
                "last_refill_ts": last_refill_ts
            }
            
            response = requests.post(CACHE_URL + "/set-cache/" + user_id, json = payload)
            response.raise_for_status()
        
        return tokens
    
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
    stamped_request = None
    try:
        stamped_request = limiter.build_record(request, COUNTER_URL)

        """
        ------------ Beginning of test code ------------
        """
        user_id = stamped_request["user_id"]
        response = limiter.fetch_tokens(user_id)
        """
        ------------ End of test code ------------
        """
            
        return jsonify(stamped_request)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == "__main__":
    app.run(port=5002, debug=True)