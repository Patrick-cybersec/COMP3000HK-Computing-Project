import json, time, hashlib, os, hmac, requests

DB_FILE = "users.json"
PAYLOAD_FILE = r"C:\Users\Patrick\BioGuard\payload.json"
API_KEY = os.environ.get("BIOGUARD_ALERT_API_KEY", "test_api_key")
HMAC_KEY = os.environ.get("BIOGUARD_ALERT_HMAC_KEY", "test_hmac_key").encode()

def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register(username, password, keystroke_profile):
    username = username.strip().lower()
    db = load_db()
    if username in db:
        raise ValueError("Username already exists")
    db[username] = {
        "password_hash": hash_password(password),
        "keystroke_profile": keystroke_profile
    }
    save_db(db)
    print(f"User {username} registered.")

def login(username, password):
    username = username.strip().lower()
    db = load_db()
    if username not in db:
        raise ValueError("No such user")
    if db[username]["password_hash"] != hash_password(password):
        raise ValueError("Invalid password")
    print(f"User {username} logged in.")
    return username, db[username]["keystroke_profile"]

def build_alert(username, anomaly_rate, window_size):
    payload = {
        "event": "anomaly_lockout",
        "user": username,
        "anomaly_rate": round(float(anomaly_rate), 4),
        "window_size": int(window_size),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "event_id": f"lockout-{int(time.time())}"
    }

    body = json.dumps(payload, separators=(",", ":")).encode()
    signature = hmac.new(HMAC_KEY, body, hashlib.sha256).hexdigest()

    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY,
        "X-Signature": signature,
    }

    r = requests.post("http://127.0.0.1:8000/alerts", data=body, headers=headers, timeout=15)
    print("Response:", r.text)
    return payload

if __name__ == "__main__":
    try:
        register("patrick", "mypassword", {"baseline": "keystroke_data"})
    except ValueError:
        print("User already exists, skipping registration.")

    user, profile = login("patrick", "mypassword")
    anomaly_rate = 0.47
    window_size = 80
    build_alert(user, anomaly_rate, window_size)
