import requests
import random
import string
import time

# URL of the Limiter service
LIMITER_URL = "http://127.0.0.1:5002/stamped-request"

def random_user_id(length=8):
    """Generate a random user ID like 'user-AB12CD34'"""
    chars = string.ascii_uppercase + string.digits
    return "user-" + "".join(random.choice(chars) for _ in range(length))

def send_request():
    user_id = random_user_id()
    payload = {"user_id": user_id}

    try:
        response = requests.post(LIMITER_URL, json=payload)
        response.raise_for_status()
        print("Payload:", payload)
        print("Response:", response.json())
        print("-" * 50)
    except requests.exceptions.RequestException as e:
        print("Request failed:", e)

if __name__ == "__main__":
    while True:
        send_request()
        # wait randomly between 1 to 5 seconds
        time.sleep(random.randint(1, 5))