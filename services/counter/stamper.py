from flask import Flask, jsonify, request
import counter as cntr
import time

app = Flask(__name__)

class Stamper:
    def __init__(self):
        # we get whenever our Counter began
        self.counter = cntr.Counter().get_counter()
        self.timestamped_record = None
    
    def validate_get(self):
        print(self.counter)
        return self.counter
    
    # the request will simply have a user_id, and a GET call.
    # this API will simply add a timestamp to the request and return it
    # as a JSON object
    def timestamp_request(self, user_id):
        record = {
            "user_id": user_id,
            "timestamp": time.time()
        }
        self.timestamped_record = record
        return record

# now we first create an instance of our class Stamper:
stamper = Stamper()

# ----- API Routes ----- #
@app.route("/validate", methods=["GET"])
def validate():
    """
    API that validates that the counter was successfully initialized.
    INTERNAL ONLY.
    """
    result = stamper.validate_get()
    return jsonify({"epoch_start": result})

@app.route("/stamp", methods=["POST"])
def stamp():
    """
    POST API that expects a JSON: {"user_id": "<user_id>"}
    """
    data = request.get_json() # get the JSON body
    # now we extract the user_id from the data:
    if not data or "user_id" not in data:
        return jsonify({"error": "Missing user_id in the request; Request Invalid"}), 400
    
    user_id = data["user_id"]
    
    # Get the timestamped record:
    record = stamper.timestamp_request(user_id)
    
    # Return our JSON immediately:
    return jsonify(record)
    
# RUN THE APP #
if __name__ == "__main__":
    app.run(port=5001, debug=True)