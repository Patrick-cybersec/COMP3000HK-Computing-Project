# bioguard_auth.py
import json, time, os, hmac, requests
import bcrypt

DB_FILE = "users.json"
API_KEY = os.environ.get("BIOGUARD_ALERT_API_KEY", "test_api_key")
HMAC_KEY = os.environ.get("BIOGUARD_ALERT_HMAC_KEY", "test_hmac_key").encode()
ADMIN_API_KEY = os.environ.get("BIOGUARD_ADMIN_API_KEY", "admin_secret_key")

def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2)

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def normalize_username(username: str) -> str:
    if username is None:
        return ""
    return username.strip().lower()

def register(username, password, keystroke_profile, role="user"):
    username = normalize_username(username)
    if not username:
        raise ValueError("Username cannot be empty")
    db = load_db()
    if username in db:
        raise ValueError("Username already exists")
    db[username] = {
        "password_hash": hash_password(password),
        "keystroke_profile": keystroke_profile,
        "role": role
    }
    save_db(db)
    print(f"User {username} registered with role {role}.")

def login(username, password):
    username = normalize_username(username)
    db = load_db()
    if username not in db:
        raise ValueError("No such user")
    if not check_password(password, db[username]["password_hash"]):
        raise ValueError("Invalid password")
    print(f"User {username} logged in.")
    return username, db[username]["keystroke_profile"], db[username].get("role", "user")

def build_alert(username, anomaly_rate, window_size, explanation=None, severity=None):
    payload = {
        "event": "anomaly_lockout",
        "user": username,
        "anomaly_rate": round(float(anomaly_rate), 4),
        "window_size": int(window_size),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "event_id": f"lockout-{int(time.time())}",
        "severity": severity or "unknown",
        "explanation": explanation or {}
    }

    body = json.dumps(payload, separators=(",", ":")).encode()
    signature = hmac.new(HMAC_KEY, body, "sha256").hexdigest()

    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY,
        "X-Signature": signature,
    }

    try:
        r = requests.post("http://127.0.0.1:8000/alerts", data=body, headers=headers, timeout=15)
        print("Response:", r.text)
    except Exception as e:
        print("Alert send failed:", e)
    return payload
