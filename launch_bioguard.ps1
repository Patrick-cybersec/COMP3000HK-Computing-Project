# Set environment variables
$env:BIOGUARD_ADMIN_URL="http://127.0.0.1:8000/alerts"
$env:BIOGUARD_ALERT_API_KEY="test_api_key"
$env:BIOGUARD_ALERT_HMAC_KEY="test_hmac_key"

# Start admin listener in background
Start-Process powershell -ArgumentList 'uvicorn admin_listener:app --reload --host 127.0.0.1 --port 8000'

# Wait a few seconds for listener to boot
Start-Sleep -Seconds 5

# Launch BioGuard client
python bioguard_ml.py
