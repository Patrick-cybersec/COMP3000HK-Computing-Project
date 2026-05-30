# BioGuard

BioGuard is a behavioral biometrics security project that leverages keystroke dynamics and machine learning to detect anomalies in user typing patterns. It integrates cryptographic storage, real‑time monitoring, and an admin dashboard to provide proactive defense against unauthorized access.

---

## 📂 Repository Structure
- `BioGuard-latest/` → **Use this folder** for the newest version of BioGuard.
- `BioGuard/` → Legacy folder (older version, kept for reference).
- `data/`, `logs/`, `secure_profiles/` → Supporting datasets and runtime outputs.
- `.gitignore` → Ensures venv, cache, and junk files are excluded.
- `requirements.txt` → Python dependencies for recreating the environment.

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/Patrick-cybersec/COMP3000HK-Computing-Project.git
cd COMP3000HK-Computing-Project/BioGuard-latest
2. Create a virtual environment
On Windows:

bash
python -m venv venv
venv\Scripts\activate
On macOS/Linux:

bash
python3 -m venv venv
source venv/bin/activate
3. Install dependencies
bash
pip install -r ../requirements.txt
4. Run BioGuard
Depending on your entry point:

bash
python bioguard_ml.py
or if using FastAPI:

bash
uvicorn admin_listener:app --reload
5. Access the dashboard
Open your browser at:

Code
http://127.0.0.1:8000
🛠 Features
Keystroke dynamics capture and anomaly detection

Secure profile storage with cryptography

Admin dashboard with FastAPI + Uvicorn

Real‑time alerts and logging

📊 Demo Workflow
Start BioGuard (python bioguard.py).

Type normally — keystroke dynamics are captured.

Anomalies trigger alerts in bioguard_alerts.log.

Admin dashboard shows live monitoring at http://127.0.0.1:8000.

⚙️ Requirements
Python 3.9+

Pip (latest version recommended)

Windows, macOS, or Linux

📌 Notes
Always activate the virtual environment before running.

Do not commit venv/ or cache files — .gitignore already excludes them.

Use requirements.txt to rebuild the environment cleanly.
