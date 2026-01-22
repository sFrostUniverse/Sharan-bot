import requests
import json

URL = "https://sharan-bot-kp71.onrender.com/eventsub"

payload = {
    "challenge": "test_challenge_12345",
    "subscription": {
        "type": "stream.online"
    }
}

headers = {
    "Content-Type": "application/json"
}

resp = requests.post(URL, headers=headers, json=payload, timeout=10)

print("STATUS:", resp.status_code)
print("RESPONSE TEXT:", resp.text)
