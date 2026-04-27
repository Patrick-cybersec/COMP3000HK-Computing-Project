import json, hmac, hashlib, requests, os

# Path to your payload file
PAYLOAD_FILE = r"C:\Users\Patrick\BioGuard\payload.json"

# Load keys (use environment variables if set, otherwise defaults)
API_KEY = os.environ.get("BIOGUARD_ALERT_API_KEY", "test_api_key")
HMAC_KEY = os.environ.get("BIOGUARD_ALERT_HMAC_KEY", "test_hmac_key").encode()

# Read payload
payload = json.load(open(PAYLOAD_FILE))
body = json.dumps(payload, separators=(",", ":")).encode()
signature = hmac.new(HMAC_KEY, body, hashlib.sha256).hexdigest()


# Send to FastAPI listener
url = "http://127.0.0.1:8000/alerts"
headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY,
    "X-Signature": signature,
}

response = requests.post(url, data=body, headers=headers)
print("Status:", response.status_code)
print("Response:", response.text)
