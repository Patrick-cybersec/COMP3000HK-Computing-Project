# admin_listener.py
from fastapi import FastAPI, Request, HTTPException
import hmac, hashlib, json, os, time
from typing import List

app = FastAPI()

API_KEY = os.environ.get("BIOGUARD_ALERT_API_KEY", "test_api_key")
HMAC_KEY = os.environ.get("BIOGUARD_ALERT_HMAC_KEY", "test_hmac_key").encode()
LOG_PATH = r"C:\Users\Patrick\BioGuard\bioguard_alerts.log"

os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

def append_log(entry: dict):
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

@app.get("/logs")
async def get_logs_alias(n: int = 100, admin_key: str = "admin_secret_key"):
    if admin_key != "admin_secret_key":
        raise HTTPException(status_code=401, detail="unauthorized")
    return await get_logs(n)


@app.post("/alerts")
async def receive_alert(request: Request):
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="bad_request")

    body = json.dumps(payload, separators=(",", ":")).encode()
    signature = hmac.new(HMAC_KEY, body, hashlib.sha256).hexdigest()

    api_key = request.headers.get("X-API-Key")
    provided_sig = request.headers.get("X-Signature")

    verified = (api_key == API_KEY and provided_sig == signature)
    entry = {
        "received_at": int(time.time()),
        "source_ip": request.client.host if request.client else None,
        "verified": verified,
        **payload
    }

    if not verified:
        append_log({**entry, "status": "ok", "verified": verified})
        raise HTTPException(status_code=401, detail="unauthorized")

    append_log({**entry, "status": "ok"})
    print("Received alert:", payload)
    return {"status": "ok", "event_id": payload.get("event_id")}

# Admin helper: return last N log lines (JSON)
@app.get("/admin/logs")
async def get_logs(n: int = 100):
    if not os.path.exists(LOG_PATH):
        return []
    lines = []
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            try:
                lines.append(json.loads(line))
            except:
                continue
    return lines[-n:]
