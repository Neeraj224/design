import requests
import random
import string
import time

# URL of the Limiter service
LIMITER_URL = "http://127.0.0.1:5002/stamped-request"

# Keep track of existing users for repeated requests
existing_users = []

def random_user_id(length=8):
    """Generate a random user ID like 'user-AB12CD34'"""
    chars = string.ascii_uppercase + string.digits
    return "user-" + "".join(random.choice(chars) for _ in range(length))

def send_request():
    # 50% chance to pick existing user, 50% chance to create new
    if existing_users and random.random() < 0.5:
        user_id = random.choice(existing_users)
        new_user = False
    else:
        user_id = random_user_id()
        existing_users.append(user_id)
        new_user = True

    payload = {"user_id": user_id}

    try:
        response = requests.post(LIMITER_URL, json=payload)
        response.raise_for_status()
        print(f"{'NEW' if new_user else 'EXISTING'} user request")
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