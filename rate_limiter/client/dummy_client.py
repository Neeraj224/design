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

def send_request(user_id, new_user):
    payload = {"user_id": user_id}

    try:
        response = requests.post(LIMITER_URL, json=payload)
        # If throttled, status_code will be 429
        if response.status_code == 429:
            print(f"THROTTLED: {user_id}")
        else:
            print(f"{'NEW' if new_user else 'EXISTING'} user request")
            print("Payload:", payload)
            print("Response:", response.json())
        print("-" * 50)
    except requests.exceptions.RequestException as e:
        print("Request failed:", e)

if __name__ == "__main__":
    while True:
        # 70% chance we generate a burst of requests from existing users
        if existing_users and random.random() < 0.7:
            burst_size = random.randint(3, 7)  # simulate a burst
            for _ in range(burst_size):
                user_id = random.choice(existing_users)
                send_request(user_id, new_user=False)
                # very short interval between burst requests
                time.sleep(random.uniform(0.1, 0.5))
        else:
            # create a new user request
            user_id = random_user_id()
            existing_users.append(user_id)
            send_request(user_id, new_user=True)
            time.sleep(random.randint(1, 3))  # normal interval for new user