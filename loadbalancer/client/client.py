import requests

def call_load_balancer():
    for i in range(10):
        resp = requests.get("http://127.0.0.1:8080/work", timeout=3)
        print(f"Request {i + 1}: {resp.status_code} -> {resp.json()}")

if __name__ == "__main__":
    call_load_balancer()