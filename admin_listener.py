from fastapi import FastAPI, Request
import hmac, hashlib, json, os, time

app = FastAPI()

API_KEY = os.environ.get("BIOGUARD_ALERT_API_KEY", "test_api_key")
HMAC_KEY = os.environ.get("BIOGUARD_ALERT_HMAC_KEY", "test_hmac_key").encode()

LOG_PATH = r"C:\Users\Patrick\BioGuard\bioguard_alerts.log"

@app.get("/ping")
async def ping():
    return {"status": "alive"}

@app.post("/alerts")
async def receive_alert(request: Request):
    try:
        payload = await request.json()
    except Exception:
        return {"status": "bad_request"}

    body = json.dumps(payload, separators=(",", ":")).encode()
    signature = hmac.new(HMAC_KEY, body, hashlib.sha256).hexdigest()

    api_key = request.headers.get("X-API-Key")
    provided_sig = request.headers.get("X-Signature")

    if api_key != API_KEY or provided_sig != signature:
        return {"status": "unauthorized"}

    # Append to permanent log file
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps({"received_at": int(time.time()), **payload}) + "\n")

    print("Received alert:", payload)
    return {"status": "ok", "event_id": payload.get("event_id")}
