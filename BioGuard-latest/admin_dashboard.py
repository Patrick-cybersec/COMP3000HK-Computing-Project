# admin_dashboard.py
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
import os, json
from typing import Optional

app = FastAPI()
LOG_PATH = r"C:\Users\Patrick\BioGuard\bioguard_alerts.log"
ADMIN_KEY = os.environ.get("BIOGUARD_ADMIN_API_KEY", "admin_secret_key")

def require_admin(request: Request):
    key = request.headers.get("X-Admin-Key") or request.query_params.get("admin_key")
    if key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="forbidden")

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    html = """
    <html><head><title>BioGuard Admin</title></head><body>
    <h1>BioGuard Admin Dashboard</h1>
    <p>Endpoints:</p>
    <ul>
      <li><a href="/logs?admin_key=REPLACE">View logs (JSON)</a></li>
    </ul>
    <p>Use the API key in header X-Admin-Key or query param admin_key.</p>
    </body></html>
    """
    return html

@app.get("/logs")
async def logs(n: int = 200, admin_key: Optional[str] = None, request: Request = None):
    # simple admin check
    key = request.headers.get("X-Admin-Key") if request else admin_key
    if key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="forbidden")
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
